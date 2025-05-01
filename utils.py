import torch
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, label_binarize
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve, f1_score, accuracy_score

import matplotlib.pyplot as plt
import logging
from itertools import cycle

logger = logging.getLogger(__name__)

def set_device(device=None) -> str:
    """Set device for pytorch"""
    if device is None:
        if torch.backends.mps.is_available():
            device = 'mps'
        elif torch.cuda.is_available():
            device = 'cuda'
        else:
            device = 'cpu'
    logger.info(f'Using device: {device}')
    return device

def label_encode_cols(df: pd.DataFrame, cols: list[str]) -> np.ndarray:
    """Encode column for a dataframe and return a numpy array"""
    if len(cols) == 1:
        cols = cols[0]
    label_encoder = LabelEncoder()
    y  = label_encoder.fit_transform(df[cols])
    return y, label_encoder.classes_

def load_dataset(fpath):
    # Load preprocessed data
    df = pd.read_csv(fpath)
    
    df['cleaned_text'] = df['cleaned_text'].astype(str)
    
    # Encode labels
    label_col = 'Bias'
    X = df['cleaned_text']
    y, classes = label_encode_cols(df, [label_col])
    
    return X, y, classes

def plot_result_curves(net, title):
    history = net.history

    fig = plt.figure(figsize=(12, 8)) 

    # Plot loss
    plt.plot(history[:, 'train_loss'], label='train loss', color='blue')
    plt.plot(history[:, 'valid_loss'], label='valid loss', color='green', linestyle='-.')
    
    # Plot accuracy
    plt.plot(history[:, 'train_acc'], label='train acc', color='magenta', linestyle='--')
    plt.plot(history[:, 'valid_acc'], label='valid acc', color='red', linestyle=':')
    
    # Plot F1
    plt.plot(history[:, 'train_f1'], label='train f1', color='cyan', linestyle='--')
    plt.plot(history[:, 'valid_f1'], label='valid f1', color='gold', linestyle=':')

    plt.title(title)
    plt.xlabel('epoch')
    plt.ylabel('metrics')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    return fig

def print_evaluation_report(y_pred, test_dataset, classes, model_name, average='weighted'):

    acc = accuracy_score(test_dataset.labels, y_pred)
    f1 = f1_score(test_dataset.labels, y_pred, average=average)
    report = classification_report(test_dataset.labels, y_pred, target_names=classes, digits=4)
    print(f"{model_name} Accuracy: {acc * 100:.2f}%")
    print(f"{model_name} Weighted F1-score: {f1:.4f}")
    print("\nClassification Report:\n", report)
    return

def plot_confusion_matrix(y_pred, test_dataset, classes, model_name):
   
    label_order = ['left', 'lean left', 'center', 'lean right', 'right']
    label_indices = [np.where(classes == label)[0][0] for label in label_order]
    
    cm = confusion_matrix(test_dataset.labels, y_pred, labels=label_indices)
    
    fig = plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=label_order, yticklabels=label_order)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title(f"{model_name} Confusion Matrix")
    plt.tight_layout()
    plt.show()
    return fig

def show_one_vs_rest_confusion_matrices(net, y_pred, test_dataset, class_names):
    classes = net.classes_
    
    for i, class_idx in enumerate(classes):
        class_label = class_names[class_idx]
        
        y_true_binary = (test_dataset.labels == class_idx).astype(int)
        y_pred_binary = (y_pred == class_idx).astype(int)
    
        cm = confusion_matrix(y_true_binary, y_pred_binary)
        print(f"\nOne-vs-Rest Confusion Matrix for class '{class_label}':")
        print(cm)


def plot_roc(y_prob, net, test_dataset, class_names, model_name):

    label_order = ['left', 'lean left', 'center', 'lean right', 'right']
    label_indices = [np.where(class_names == label)[0][0] for label in label_order]
    
    y_test_binarized = label_binarize(test_dataset.labels, classes=range(len(net.classes_)))
    
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    
    # Compute ROC data
    for label, idx in zip(label_order, label_indices):
        fpr[label], tpr[label], _ = roc_curve(y_test_binarized[:, idx], y_prob[:, idx])
        roc_auc[label] = roc_auc_score(y_test_binarized[:, idx], y_prob[:, idx])
    
    # Plot
    fig = plt.figure(figsize=(10, 8))
    colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'red', 'green', 'purple', 'brown'])
    
    for label, color in zip(label_order, colors):
        plt.plot(fpr[label], tpr[label], color=color, lw=2,
                 label=f'ROC for class {label} (AUC = {roc_auc[label]:.2f})')
    
    plt.plot([0, 1], [0, 1], 'k--', lw=1)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'{model_name} One-vs-Rest ROC Curves')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.show()
    return fig