import numpy as np
import pandas as pd


class HardCodedNaiveBayes:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.classes_ = None
        self.class_log_prior_ = None
        self.feature_log_prob_ = None
        self.feature_names_ = None

    def _binarize_features(self, X):
        if self.feature_names_ is None:
            self.feature_names_ = [c for c in X.columns if c.startswith("tfidf_")]
        X_bin = X[self.feature_names_]
        return (X_bin > 0).astype(int).values

    def fit(self, X, y):
        X_bin = self._binarize_features(X)
        n_samples, n_features = X_bin.shape
        y = np.array(y)

        self.classes_ = np.sort(np.unique(y))

        self.class_log_prior_ = {}
        self.feature_log_prob_ = {}

        for c in self.classes_:
            mask = y == c
            n_c = np.sum(mask)

            self.class_log_prior_[c] = np.log(n_c / n_samples)

            feature_counts = np.sum(X_bin[mask], axis=0)
            total_words = np.sum(feature_counts)

            log_prob = np.log(feature_counts + self.alpha) - np.log(
                total_words + self.alpha * n_features
            )
            self.feature_log_prob_[c] = log_prob

        return self

    def predict(self, X):
        proba = self.predict_proba(X)
        indices = np.argmax(proba, axis=1)
        return np.array([self.classes_[i] for i in indices])

    def predict_proba(self, X):
        X_bin = self._binarize_features(X)
        n_samples = X_bin.shape[0]
        n_classes = len(self.classes_)

        log_prob = np.zeros((n_samples, n_classes))

        for i, c in enumerate(self.classes_):
            log_prob[:, i] = (
                self.class_log_prior_[c] + X_bin @ self.feature_log_prob_[c]
            )

        log_prob_max = np.max(log_prob, axis=1, keepdims=True)
        log_prob_stable = log_prob - log_prob_max
        prob = np.exp(log_prob_stable)
        prob /= np.sum(prob, axis=1, keepdims=True)

        return prob


def accuracy_score(y_true, y_pred):
    return np.mean(y_true == y_pred)


def compute_confusion_matrix(y_true, y_pred, classes):
    n = len(classes)
    cm = np.zeros((n, n), dtype=int)
    class_to_idx = {c: i for i, c in enumerate(classes)}
    for t, p in zip(y_true, y_pred):
        cm[class_to_idx[t], class_to_idx[p]] += 1
    return cm


def compute_precision_recall_f1(cm, classes):
    n = len(classes)
    precision = {}
    recall = {}
    f1 = {}

    for i, c in enumerate(classes):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp

        precision[c] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall[c] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        denom = precision[c] + recall[c]
        f1[c] = 2 * precision[c] * recall[c] / denom if denom > 0 else 0.0

    macro_precision = np.mean(list(precision.values()))
    macro_recall = np.mean(list(recall.values()))
    macro_f1 = np.mean(list(f1.values()))

    return precision, recall, f1, macro_precision, macro_recall, macro_f1


def main():
    from collections import Counter

    df = pd.read_csv("data/processed/ml_features.csv")

    feature_cols = [c for c in df.columns if c.startswith("tfidf_")]
    X = df[feature_cols]
    y = df["rating"].values

    n = len(df)
    np.random.seed(42)
    indices = np.random.permutation(n)
    split_idx = int(0.8 * n)
    train_idx, test_idx = indices[:split_idx], indices[split_idx:]

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    model = HardCodedNaiveBayes(alpha=1.0)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    most_common_class = Counter(y_train).most_common(1)[0][0]
    y_baseline = np.full_like(y_test, most_common_class)

    acc_model = accuracy_score(y_test, y_pred)
    acc_baseline = accuracy_score(y_test, y_baseline)

    cm = compute_confusion_matrix(y_test, y_pred, model.classes_)
    precision, recall, f1, macro_p, macro_r, macro_f = compute_precision_recall_f1(
        cm, model.classes_
    )

    classes = model.classes_

    print("=" * 70)
    print("MULTINOMIAL NAIVE BAYES — IMPLEMENTACAO HARD-CODE")
    print("=" * 70)
    print(f"\nAcuracia: {acc_model:.4f}")
    print(f"Acuracia Baseline (classe {most_common_class}): {acc_baseline:.4f}")
    print(f"\nPrecision (macro): {macro_p:.4f}")
    print(f"Recall (macro):    {macro_r:.4f}")
    print(f"F1-Score (macro):  {macro_f:.4f}")

    print(f"\n{'Classe':<8} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 44)
    for c in classes:
        print(f"{c:<8} {precision[c]:<12.4f} {recall[c]:<12.4f} {f1[c]:<12.4f}")

    print("\nMatriz de Confusao (linha=real, coluna=predito):")
    header = "       " + "".join(f"{int(c):>6}" for c in classes)
    print(header)
    for i, c in enumerate(classes):
        row = f"{int(c):>6}" + "".join(f"{cm[i, j]:>6}" for j in range(len(classes)))
        print(row)

    cm_baseline = compute_confusion_matrix(y_test, y_baseline, classes)
    _, _, _, bp, br, bf = compute_precision_recall_f1(cm_baseline, classes)

    print(f"\n{'Metrica':<25} {'Baseline':<12} {'Hard-Code NB':<12}")
    print("-" * 49)
    print(f"{'Acuracia':<25} {acc_baseline:<12.4f} {acc_model:<12.4f}")
    print(f"{'Precision (macro)':<25} {bp:<12.4f} {macro_p:<12.4f}")
    print(f"{'Recall (macro)':<25} {br:<12.4f} {macro_r:<12.4f}")
    print(f"{'F1-Score (macro)':<25} {bf:<12.4f} {macro_f:<12.4f}")


if __name__ == "__main__":
    main()
