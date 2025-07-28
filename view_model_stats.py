#!/usr/bin/env python3
"""
Script to view model performance statistics.
Usage: python view_model_stats.py
"""

import json
from pathlib import Path
from ml.model_trainer import ModelTrainer
from config import MODEL_STATS_FILE

def main():
    """Display model statistics."""
    print("📊 League Data Farm - Model Statistics Viewer")
    print("=" * 60)
    
    try:
        # Load model trainer to access statistics methods
        trainer = ModelTrainer()
        
        # Print statistics
        trainer.print_model_statistics()
        
        # Show detailed statistics if available
        stats = trainer.load_model_statistics()
        
        if stats:
            print(f"\n📈 Detailed Statistics ({len(stats)} models tracked)")
            print("=" * 60)
            
            # Show performance trends
            print("\n🎯 Performance Trends:")
            print("-" * 30)
            
            for i, stat in enumerate(stats[-5:], 1):  # Last 5 models
                metrics = stat['performance_metrics']
                version = stat['model_version']
                timestamp = stat['timestamp'][:19]  # Remove microseconds
                
                print(f"Model {i}: {version} ({timestamp})")
                print(f"  Test Accuracy: {metrics['test_accuracy']:.3f}")
                print(f"  ROC AUC: {metrics['roc_auc_score']:.3f}")
                print(f"  CV Score: {metrics['cross_validation_mean']:.3f} ± {metrics['cross_validation_std']:.3f}")
                
                data_summary = stat['data_summary']
                print(f"  Data: {data_summary.get('total_matches', 'N/A')} matches")
                print()
            
            # Show latest model details
            latest = stats[-1]
            print("🏆 Latest Model Details:")
            print("-" * 30)
            
            metrics = latest['performance_metrics']
            model_info = latest['model_info']
            feature_importance = latest['feature_importance']
            
            print(f"Version: {latest['model_version']}")
            print(f"Trained: {latest['timestamp']}")
            print(f"Test Accuracy: {metrics['test_accuracy']:.1%}")
            print(f"Train Accuracy: {metrics['train_accuracy']:.1%}")
            print(f"ROC AUC: {metrics['roc_auc_score']:.3f}")
            print(f"Cross-Validation: {metrics['cross_validation_mean']:.3f} ± {metrics['cross_validation_std']:.3f}")
            print(f"Features: {model_info['n_features']}")
            print(f"Training Samples: {model_info['n_samples_train']}")
            print(f"Test Samples: {model_info['n_samples_test']}")
            
            # Show top features
            print(f"\n🔝 Top 5 Most Important Features:")
            print("-" * 30)
            feature_names = [
                'championName', 'role', 'kda', 'damage_per_min', 'vision_per_min',
                'goldPerMinute', 'killParticipation', 'maxCsAdvantageOnLaneOpponent',
                'maxLevelLeadLaneOpponent', 'visionScoreAdvantageLaneOpponent',
                'skillshotsHit', 'skillshotsDodged', 'teamDamagePercentage',
                'damageTakenOnTeamPercentage', 'controlWardTimeCoverageInRiverOrEnemyHalf'
            ]
            
            top_indices = feature_importance['top_5_features']
            importance_scores = feature_importance['importance_scores']
            
            for i, idx in enumerate(reversed(top_indices), 1):
                feature_name = feature_names[idx] if idx < len(feature_names) else f"Feature_{idx}"
                importance = importance_scores[idx]
                print(f"{i}. {feature_name}: {importance:.3f}")
            
            # Performance assessment
            print(f"\n📊 Performance Assessment:")
            print("-" * 30)
            
            test_acc = metrics['test_accuracy']
            roc_auc = metrics['roc_auc_score']
            
            if test_acc > 0.8:
                print("✅ Excellent performance (>80% accuracy)")
            elif test_acc > 0.7:
                print("🟢 Good performance (70-80% accuracy)")
            elif test_acc > 0.6:
                print("🟡 Fair performance (60-70% accuracy)")
            else:
                print("🔴 Poor performance (<60% accuracy)")
            
            if roc_auc > 0.8:
                print("✅ Excellent discrimination (ROC AUC > 0.8)")
            elif roc_auc > 0.7:
                print("🟢 Good discrimination (ROC AUC 0.7-0.8)")
            elif roc_auc > 0.6:
                print("🟡 Fair discrimination (ROC AUC 0.6-0.7)")
            else:
                print("🔴 Poor discrimination (ROC AUC < 0.6)")
                
        else:
            print("❌ No model statistics found.")
            print("Train a model first to see statistics.")
            
    except Exception as e:
        print(f"❌ Error viewing model statistics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 