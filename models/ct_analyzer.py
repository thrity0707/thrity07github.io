#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CT影像分析AI模型
CT Image Analysis AI Model
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import cv2
from monai.networks.nets import DenseNet121, UNet
from monai.networks.layers import Norm

logger = logging.getLogger(__name__)

class CTClassificationModel(nn.Module):
    """CT分类模型"""
    
    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        super(CTClassificationModel, self).__init__()
        
        # 使用MONAI的DenseNet121作为backbone
        self.backbone = DenseNet121(
            spatial_dims=2,
            in_channels=1,
            out_channels=num_classes,
            pretrained=pretrained
        )
        
        self.num_classes = num_classes
        
    def forward(self, x):
        return self.backbone(x)

class CTSegmentationModel(nn.Module):
    """CT分割模型"""
    
    def __init__(self, num_classes: int = 2):
        super(CTSegmentationModel, self).__init__()
        
        # 使用MONAI的UNet
        self.unet = UNet(
            spatial_dims=2,
            in_channels=1,
            out_channels=num_classes,
            channels=(16, 32, 64, 128, 256),
            strides=(2, 2, 2, 2),
            num_res_units=2,
            norm=Norm.BATCH,
        )
        
    def forward(self, x):
        return self.unet(x)

class CTAnalyzer:
    """CT影像分析器"""
    
    def __init__(self, device: str = 'auto'):
        """初始化分析器"""
        self.device = self._get_device(device)
        self.classification_model = None
        self.segmentation_model = None
        self.is_classification_loaded = False
        self.is_segmentation_loaded = False
        
        # 分析结果缓存
        self.last_analysis_result = None
        
    def _get_device(self, device: str) -> torch.device:
        """获取计算设备"""
        if device == 'auto':
            if torch.cuda.is_available():
                device = 'cuda'
                logger.info("使用GPU进行计算")
            else:
                device = 'cpu'
                logger.info("使用CPU进行计算")
        
        return torch.device(device)
    
    def load_classification_model(self, model_path: Optional[str] = None, num_classes: int = 2):
        """加载分类模型"""
        try:
            self.classification_model = CTClassificationModel(num_classes=num_classes)
            
            if model_path and torch.cuda.is_available():
                # 如果有预训练模型路径，加载权重
                state_dict = torch.load(model_path, map_location=self.device)
                self.classification_model.load_state_dict(state_dict)
                logger.info(f"成功加载分类模型: {model_path}")
            else:
                logger.info("使用预训练的分类模型")
            
            self.classification_model.to(self.device)
            self.classification_model.eval()
            self.is_classification_loaded = True
            
        except Exception as e:
            logger.error(f"加载分类模型失败: {str(e)}")
            self.is_classification_loaded = False
    
    def load_segmentation_model(self, model_path: Optional[str] = None, num_classes: int = 2):
        """加载分割模型"""
        try:
            self.segmentation_model = CTSegmentationModel(num_classes=num_classes)
            
            if model_path and torch.cuda.is_available():
                state_dict = torch.load(model_path, map_location=self.device)
                self.segmentation_model.load_state_dict(state_dict)
                logger.info(f"成功加载分割模型: {model_path}")
            else:
                logger.info("使用默认的分割模型")
            
            self.segmentation_model.to(self.device)
            self.segmentation_model.eval()
            self.is_segmentation_loaded = True
            
        except Exception as e:
            logger.error(f"加载分割模型失败: {str(e)}")
            self.is_segmentation_loaded = False
    
    def classify_image(self, image: np.ndarray) -> Dict:
        """
        对CT图像进行分类
        Classify CT image
        
        Args:
            image: 预处理后的图像数组
            
        Returns:
            分类结果字典
        """
        if not self.is_classification_loaded:
            self.load_classification_model()
        
        try:
            # 数据预处理
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=0)  # 添加通道维度
            
            # 转换为tensor
            image_tensor = torch.from_numpy(image).float()
            image_tensor = image_tensor.unsqueeze(0).to(self.device)  # 添加batch维度
            
            # 推理
            with torch.no_grad():
                outputs = self.classification_model(image_tensor)
                probabilities = F.softmax(outputs, dim=1)
                prediction = torch.argmax(probabilities, dim=1)
            
            # 结果解析
            prob_values = probabilities.cpu().numpy()[0]
            pred_class = prediction.cpu().numpy()[0]
            
            # 类别标签
            class_labels = {0: '正常', 1: '异常'}
            
            result = {
                'prediction': int(pred_class),
                'prediction_label': class_labels.get(pred_class, '未知'),
                'confidence': float(prob_values[pred_class]),
                'probabilities': {
                    class_labels[i]: float(prob_values[i]) 
                    for i in range(len(prob_values))
                },
                'analysis_type': 'classification'
            }
            
            logger.info(f"分类结果: {result['prediction_label']}, 置信度: {result['confidence']:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"分类分析失败: {str(e)}")
            return {'error': str(e), 'analysis_type': 'classification'}
    
    def segment_image(self, image: np.ndarray) -> Dict:
        """
        对CT图像进行分割
        Segment CT image
        
        Args:
            image: 预处理后的图像数组
            
        Returns:
            分割结果字典
        """
        if not self.is_segmentation_loaded:
            self.load_segmentation_model()
        
        try:
            # 数据预处理
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=0)
            
            image_tensor = torch.from_numpy(image).float()
            image_tensor = image_tensor.unsqueeze(0).to(self.device)
            
            # 推理
            with torch.no_grad():
                outputs = self.segmentation_model(image_tensor)
                segmentation = torch.argmax(outputs, dim=1)
            
            # 转换回numpy
            seg_result = segmentation.cpu().numpy()[0]
            
            # 计算分割统计
            unique_labels, counts = np.unique(seg_result, return_counts=True)
            total_pixels = seg_result.size
            
            segment_stats = {}
            for label, count in zip(unique_labels, counts):
                percentage = (count / total_pixels) * 100
                segment_stats[f'类别_{label}'] = {
                    'pixel_count': int(count),
                    'percentage': float(percentage)
                }
            
            result = {
                'segmentation_mask': seg_result,
                'segment_statistics': segment_stats,
                'total_pixels': total_pixels,
                'analysis_type': 'segmentation'
            }
            
            logger.info(f"分割完成，检测到 {len(unique_labels)} 个区域")
            return result
            
        except Exception as e:
            logger.error(f"分割分析失败: {str(e)}")
            return {'error': str(e), 'analysis_type': 'segmentation'}
    
    def generate_heatmap(self, image: np.ndarray, method: str = 'gradcam') -> np.ndarray:
        """
        生成热力图
        Generate heatmap
        
        Args:
            image: 输入图像
            method: 热力图生成方法
            
        Returns:
            热力图数组
        """
        try:
            if not self.is_classification_loaded:
                self.load_classification_model()
            
            # 简化的热力图生成（基于梯度）
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=0)
            
            image_tensor = torch.from_numpy(image).float()
            image_tensor = image_tensor.unsqueeze(0).to(self.device)
            image_tensor.requires_grad_()
            
            # 前向传播
            outputs = self.classification_model(image_tensor)
            
            # 反向传播获取梯度
            self.classification_model.zero_grad()
            outputs.max().backward()
            
            # 生成热力图
            gradients = image_tensor.grad.data.abs()
            heatmap = gradients.cpu().numpy()[0, 0]
            
            # 归一化到0-255
            heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())
            heatmap = (heatmap * 255).astype(np.uint8)
            
            # 应用颜色映射
            heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            
            logger.info("热力图生成完成")
            return heatmap_colored
            
        except Exception as e:
            logger.error(f"热力图生成失败: {str(e)}")
            return np.zeros_like(image, dtype=np.uint8)
    
    def comprehensive_analysis(self, image: np.ndarray) -> Dict:
        """
        综合分析
        Comprehensive analysis
        
        Args:
            image: 预处理后的图像
            
        Returns:
            综合分析结果
        """
        try:
            results = {
                'timestamp': np.datetime64('now').astype(str),
                'image_shape': image.shape
            }
            
            # 执行分类
            classification_result = self.classify_image(image)
            results['classification'] = classification_result
            
            # 执行分割
            segmentation_result = self.segment_image(image)
            results['segmentation'] = segmentation_result
            
            # 生成热力图
            heatmap = self.generate_heatmap(image)
            results['heatmap'] = heatmap
            
            # 风险评估
            risk_level = self._assess_risk(classification_result, segmentation_result)
            results['risk_assessment'] = risk_level
            
            self.last_analysis_result = results
            logger.info("综合分析完成")
            
            return results
            
        except Exception as e:
            logger.error(f"综合分析失败: {str(e)}")
            return {'error': str(e)}
    
    def _assess_risk(self, classification_result: Dict, segmentation_result: Dict) -> Dict:
        """风险评估"""
        try:
            risk_score = 0.0
            risk_factors = []
            
            # 基于分类结果评估
            if 'confidence' in classification_result:
                if classification_result['prediction'] == 1:  # 异常
                    risk_score += classification_result['confidence'] * 0.7
                    risk_factors.append(f"分类检测异常 (置信度: {classification_result['confidence']:.3f})")
            
            # 基于分割结果评估
            if 'segment_statistics' in segmentation_result:
                stats = segmentation_result['segment_statistics']
                for segment, info in stats.items():
                    if '1' in segment and info['percentage'] > 5:  # 异常区域超过5%
                        risk_score += 0.3
                        risk_factors.append(f"检测到异常区域: {info['percentage']:.1f}%")
            
            # 风险等级分类
            if risk_score >= 0.8:
                risk_level = "高风险"
            elif risk_score >= 0.5:
                risk_level = "中风险"
            elif risk_score >= 0.2:
                risk_level = "低风险"
            else:
                risk_level = "正常"
            
            return {
                'risk_score': float(risk_score),
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'recommendation': self._get_recommendation(risk_level)
            }
            
        except Exception as e:
            logger.error(f"风险评估失败: {str(e)}")
            return {'error': str(e)}
    
    def _get_recommendation(self, risk_level: str) -> str:
        """获取建议"""
        recommendations = {
            "高风险": "建议立即就医，进行进一步检查和治疗",
            "中风险": "建议咨询专业医生，考虑进一步检查",
            "低风险": "建议定期复查，注意观察症状变化",
            "正常": "继续保持健康生活方式，定期体检"
        }
        return recommendations.get(risk_level, "请咨询专业医生")
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        return {
            'classification_loaded': self.is_classification_loaded,
            'segmentation_loaded': self.is_segmentation_loaded,
            'device': str(self.device),
            'torch_version': torch.__version__,
            'cuda_available': torch.cuda.is_available()
        } 