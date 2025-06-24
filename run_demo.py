#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学影像CT分析系统演示脚本
Medical Image CT Analysis System Demo Script
"""

import sys
import os
import logging
import argparse
from datetime import datetime

def setup_demo_logging():
    """设置演示日志"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """检查依赖库"""
    dependencies = {
        'numpy': 'pip install numpy',
        'opencv-python': 'pip install opencv-python',
        'pydicom': 'pip install pydicom',
        'nibabel': 'pip install nibabel',
        'matplotlib': 'pip install matplotlib',
        'torch': 'pip install torch',
        'monai': 'pip install monai',
        'PySide6': 'pip install PySide6',
        'reportlab': 'pip install reportlab',
        'scikit-image': 'pip install scikit-image'
    }
    
    missing_deps = []
    for dep, install_cmd in dependencies.items():
        try:
            __import__(dep.replace('-', '_'))
            print(f"✓ {dep} - 已安装")
        except ImportError:
            print(f"✗ {dep} - 未安装 ({install_cmd})")
            missing_deps.append((dep, install_cmd))
    
    return missing_deps

def create_sample_data():
    """创建示例数据"""
    try:
        import numpy as np
        
        # 创建示例CT图像数据
        sample_image = np.random.randint(0, 255, (512, 512), dtype=np.uint8)
        
        # 添加一些模拟的异常区域
        sample_image[200:250, 200:250] = 180  # 高密度区域
        sample_image[300:320, 300:320] = 50   # 低密度区域
        
        return sample_image
        
    except ImportError:
        print("NumPy未安装，无法创建示例数据")
        return None

def simulate_analysis():
    """模拟分析过程"""
    print("\n=== 模拟CT影像分析过程 ===")
    
    # 模拟加载影像
    print("1. 加载CT影像...")
    print("   - 文件格式: DICOM")
    print("   - 图像尺寸: 512x512")
    print("   - 像素间距: 0.5mm x 0.5mm")
    
    # 模拟预处理
    print("\n2. 图像预处理...")
    print("   - 强度归一化")
    print("   - 尺寸标准化")
    print("   - 噪声滤除")
    
    # 模拟AI分析
    print("\n3. AI智能分析...")
    print("   - 加载预训练模型")
    print("   - 特征提取")
    print("   - 分类预测")
    print("   - 区域分割")
    print("   - 热力图生成")
    
    # 模拟结果
    print("\n4. 分析结果:")
    print("   分类结果: 正常")
    print("   置信度: 89.2%")
    print("   风险等级: 低风险")
    print("   检测区域: 2个")
    
    # 模拟风险评估
    print("\n5. 风险评估:")
    print("   - 无明显异常发现")
    print("   - 建议: 继续保持健康生活方式，定期体检")
    
    return {
        'classification': {
            'prediction_label': '正常',
            'confidence': 0.892,
            'probabilities': {'正常': 0.892, '异常': 0.108}
        },
        'risk_assessment': {
            'risk_level': '低风险',
            'risk_score': 0.15,
            'recommendation': '继续保持健康生活方式，定期体检'
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generate_demo_report(analysis_result):
    """生成演示报告"""
    report = f"""
=== 医学影像CT分析报告 ===

分析时间: {analysis_result['timestamp']}
系统版本: v2.1.3.20250321_alpha

## 分析结果
诊断结果: {analysis_result['classification']['prediction_label']}
置信度: {analysis_result['classification']['confidence']:.1%}

各类别概率:
- 正常: {analysis_result['classification']['probabilities']['正常']:.1%}
- 异常: {analysis_result['classification']['probabilities']['异常']:.1%}

## 风险评估
风险等级: {analysis_result['risk_assessment']['risk_level']}
风险评分: {analysis_result['risk_assessment']['risk_score']:.2f}

建议: {analysis_result['risk_assessment']['recommendation']}

## 技术信息
- 使用模型: DenseNet121 + UNet
- 计算设备: CPU/GPU自适应
- 处理时间: < 30秒
- 支持格式: DICOM, NIfTI, PNG, JPG

注意: 此报告仅供参考，最终诊断请咨询专业医生。
"""
    
    return report

def save_demo_report(report_content):
    """保存演示报告"""
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(output_dir, f"demo_report_{timestamp}.txt")
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n报告已保存到: {report_path}")
        return report_path
    except Exception as e:
        print(f"保存报告失败: {e}")
        return None

def run_gui_demo():
    """运行GUI演示"""
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        from gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # 检查依赖
        missing_deps = check_dependencies()
        if missing_deps:
            msg = "检测到缺少以下依赖库:\n\n"
            for dep, cmd in missing_deps[:5]:  # 只显示前5个
                msg += f"• {dep}\n"
            msg += "\n系统将以演示模式运行。"
            
            QMessageBox.information(None, "依赖检查", msg)
        
        # 启动主窗口
        window = MainWindow()
        window.show()
        
        return app.exec()
        
    except ImportError as e:
        print(f"GUI模块导入失败: {e}")
        print("请确保已安装PySide6: pip install PySide6")
        return 1

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='医学影像CT分析系统演示')
    parser.add_argument('--mode', choices=['gui', 'cli', 'check'], default='gui',
                       help='运行模式: gui(图形界面), cli(命令行), check(检查依赖)')
    parser.add_argument('--simulate', action='store_true',
                       help='运行模拟分析演示')
    
    args = parser.parse_args()
    
    logger = setup_demo_logging()
    logger.info("医学影像CT分析系统演示启动")
    
    print("=" * 60)
    print("医学影像CT分析系统 v2.1.3.20250321_alpha")
    print("Medical Image CT Analysis System")
    print("=" * 60)
    
    if args.mode == 'check':
        print("\n检查系统依赖...")
        missing_deps = check_dependencies()
        if not missing_deps:
            print("\n✓ 所有依赖库已安装，系统可以正常运行！")
        else:
            print(f"\n⚠ 发现 {len(missing_deps)} 个缺失的依赖库")
            print("请安装缺失的库后重新运行系统")
        return 0
    
    elif args.mode == 'cli' or args.simulate:
        print("\n运行命令行演示模式...")
        
        # 运行模拟分析
        analysis_result = simulate_analysis()
        
        # 生成报告
        report = generate_demo_report(analysis_result)
        print(report)
        
        # 保存报告
        save_demo_report(report)
        
        print("\n演示完成！")
        return 0
    
    elif args.mode == 'gui':
        print("\n启动图形界面...")
        return run_gui_demo()
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        sys.exit(1) 