#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学影像处理核心模块
Medical Image Processing Core Module
"""

import numpy as np
import cv2
import pydicom
import nibabel as nib
from PIL import Image
import logging
import os
from typing import Union, Tuple, Optional
import SimpleITK as sitk
from monai.transforms import (
    Compose, LoadImage, ScaleIntensity, Resize, ToTensor, 
    NormalizeIntensity, SpatialPad, CenterSpatialCrop
)

logger = logging.getLogger(__name__)

class MedicalImageProcessor:
    """医学影像处理器"""
    
    def __init__(self):
        """初始化影像处理器"""
        self.supported_formats = ['.dcm', '.dicom', '.nii', '.nii.gz', '.png', '.jpg', '.jpeg']
        self.current_image = None
        self.current_image_path = None
        self.image_metadata = {}
        
        # MONAI预处理流水线
        self.transforms = Compose([
            LoadImage(image_only=True),
            ScaleIntensity(),
            ToTensor()
        ])
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        加载医学影像
        Load medical image
        
        Args:
            image_path: 影像文件路径
            
        Returns:
            影像数据数组或None
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"文件不存在: {image_path}")
                return None
            
            file_ext = os.path.splitext(image_path.lower())[1]
            
            if file_ext in ['.dcm', '.dicom']:
                return self._load_dicom(image_path)
            elif file_ext in ['.nii', '.gz']:
                return self._load_nifti(image_path)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                return self._load_standard_image(image_path)
            else:
                logger.error(f"不支持的文件格式: {file_ext}")
                return None
                
        except Exception as e:
            logger.error(f"加载影像失败: {str(e)}")
            return None
    
    def _load_dicom(self, dicom_path: str) -> np.ndarray:
        """加载DICOM文件"""
        try:
            # 使用pydicom加载
            dicom_data = pydicom.dcmread(dicom_path)
            image_array = dicom_data.pixel_array.astype(np.float32)
            
            # 提取元数据
            self.image_metadata = {
                'PatientName': str(dicom_data.get('PatientName', 'Unknown')),
                'PatientID': str(dicom_data.get('PatientID', 'Unknown')),
                'StudyDate': str(dicom_data.get('StudyDate', 'Unknown')),
                'Modality': str(dicom_data.get('Modality', 'Unknown')),
                'SliceThickness': float(dicom_data.get('SliceThickness', 0)),
                'PixelSpacing': dicom_data.get('PixelSpacing', [1.0, 1.0]),
                'ImageShape': image_array.shape
            }
            
            # 应用窗宽窗位
            if hasattr(dicom_data, 'WindowCenter') and hasattr(dicom_data, 'WindowWidth'):
                window_center = float(dicom_data.WindowCenter)
                window_width = float(dicom_data.WindowWidth)
                image_array = self._apply_window(image_array, window_center, window_width)
            
            self.current_image = image_array
            self.current_image_path = dicom_path
            
            logger.info(f"成功加载DICOM文件: {dicom_path}")
            return image_array
            
        except Exception as e:
            logger.error(f"加载DICOM文件失败: {str(e)}")
            raise
    
    def _load_nifti(self, nifti_path: str) -> np.ndarray:
        """加载NIfTI文件"""
        try:
            nii_img = nib.load(nifti_path)
            image_array = nii_img.get_fdata().astype(np.float32)
            
            # 提取元数据
            self.image_metadata = {
                'Shape': image_array.shape,
                'Affine': nii_img.affine.tolist(),
                'Header': dict(nii_img.header),
                'PixelDims': nii_img.header.get_zooms()
            }
            
            self.current_image = image_array
            self.current_image_path = nifti_path
            
            logger.info(f"成功加载NIfTI文件: {nifti_path}")
            return image_array
            
        except Exception as e:
            logger.error(f"加载NIfTI文件失败: {str(e)}")
            raise
    
    def _load_standard_image(self, image_path: str) -> np.ndarray:
        """加载标准图像文件"""
        try:
            image = Image.open(image_path)
            image_array = np.array(image, dtype=np.float32)
            
            # 转换为灰度图（如果是彩色）
            if len(image_array.shape) == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            self.image_metadata = {
                'Shape': image_array.shape,
                'Format': image.format,
                'Mode': image.mode
            }
            
            self.current_image = image_array
            self.current_image_path = image_path
            
            logger.info(f"成功加载图像文件: {image_path}")
            return image_array
            
        except Exception as e:
            logger.error(f"加载图像文件失败: {str(e)}")
            raise
    
    def _apply_window(self, image: np.ndarray, center: float, width: float) -> np.ndarray:
        """应用窗宽窗位"""
        min_val = center - width / 2
        max_val = center + width / 2
        
        windowed = np.clip(image, min_val, max_val)
        windowed = (windowed - min_val) / (max_val - min_val) * 255
        
        return windowed.astype(np.uint8)
    
    def preprocess_for_analysis(self, target_size: Tuple[int, int] = (512, 512)) -> np.ndarray:
        """
        为分析预处理图像
        Preprocess image for analysis
        """
        if self.current_image is None:
            raise ValueError("没有加载的图像")
        
        try:
            # 归一化
            normalized = self._normalize_intensity(self.current_image)
            
            # 调整大小
            if len(normalized.shape) == 2:
                resized = cv2.resize(normalized, target_size)
            else:
                # 3D图像处理
                resized = self._resize_3d(normalized, target_size)
            
            # 确保数据类型
            processed = resized.astype(np.float32)
            
            logger.info(f"图像预处理完成，输出尺寸: {processed.shape}")
            return processed
            
        except Exception as e:
            logger.error(f"图像预处理失败: {str(e)}")
            raise
    
    def _normalize_intensity(self, image: np.ndarray) -> np.ndarray:
        """强度归一化"""
        if image.max() > image.min():
            return (image - image.min()) / (image.max() - image.min())
        else:
            return image
    
    def _resize_3d(self, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """3D图像大小调整"""
        if len(image.shape) == 3:
            # 对每个切片进行调整
            resized_slices = []
            for i in range(image.shape[2]):
                slice_img = image[:, :, i]
                resized_slice = cv2.resize(slice_img, target_size)
                resized_slices.append(resized_slice)
            return np.stack(resized_slices, axis=2)
        else:
            return cv2.resize(image, target_size)
    
    def get_image_statistics(self) -> dict:
        """获取图像统计信息"""
        if self.current_image is None:
            return {}
        
        stats = {
            'shape': self.current_image.shape,
            'dtype': str(self.current_image.dtype),
            'min_value': float(np.min(self.current_image)),
            'max_value': float(np.max(self.current_image)),
            'mean_value': float(np.mean(self.current_image)),
            'std_value': float(np.std(self.current_image)),
            'unique_values': int(len(np.unique(self.current_image)))
        }
        
        return stats
    
    def extract_roi(self, coordinates: Tuple[int, int, int, int]) -> np.ndarray:
        """
        提取感兴趣区域
        Extract Region of Interest
        
        Args:
            coordinates: (x, y, width, height)
            
        Returns:
            ROI图像数据
        """
        if self.current_image is None:
            raise ValueError("没有加载的图像")
        
        x, y, w, h = coordinates
        roi = self.current_image[y:y+h, x:x+w]
        
        logger.info(f"提取ROI: {coordinates}, 大小: {roi.shape}")
        return roi 