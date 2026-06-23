import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# ==========================================
# 1. SYNTHETIC DATA GENERATION (Kenyan Context)
# ==========================================
def generate_synthetic_data(num_records=200):
    np.random.seed(42)

    applicant_id = [f"APP_{1000+i}" for i in range(num_records)]
    age = np.random.randint(21, 65, size=num_records)
    gender = np.random.choice(['M', 'F'], size=num_records)
    employment_status = np.random.choice(['Employed', 'Self-Employed', 'Unemployed'], size=num_records, p=[0.6, 0.3, 0.1])

    # Incomes in KSh (Realistic distributions)
    monthly_income = np.random.randint(20000, 250000, size=num_records)
    loan_amount = np.random.randint(50000, 1500000, size=num_records)
    loan_term_months = np.random.choice([12, 24, 36, 48, 60], size=num_records)
    credit_history = np.random.choice(['Good', 'Poor'], size=num_records, p=[0.7, 0.3])
    existing_debts = np.random.randint(0, 300000, size=num_records)

    # Logic to roughly ensure ~30% default rate based on risk factors
    default = []
    for i in range(num_records):
        score = 0
        if credit_history[i] == 'Poor': score += 4
        if employment_status[i] == 'Unemployed': score += 3
        if loan_amount[i] > (monthly_income[i] * 12): score += 2
        if existing_debts[i] > 150000: score += 1

        # Threshold for default
        if score >= 4 or (score >= 2 and np.random.rand() > 0.5):
            default.append('Yes')
        else:
            default.append('No')

    # Pad/adjust to secure close to 30% default rate
    df = pd.DataFrame({
        'applicant_id': applicant_id,
        'age': age,
        'gender': gender,
        'employment_status': employment_status,
        'monthly_income': monthly_income,
        'loan_amount': loan_amount,
        'loan_term_months': loan_term_months,
        'credit_history': credit_history,
        'existing_debts': existing_debts,
        'default': default
    })

    # Intentionally inject a few missing values to showcase handling
    df.loc[np.random.choice(df.index, 5), 'monthly_income'] = np.nan
    return df


# ==========================================
# 2. OOP CODEBASE: LOAN RISK PREDICTOR CLASS
# ==========================================
class LoanRiskPredictor:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.models = {
            'KNN': None,
            'NaiveBayes': GaussianNB()
        }
        self.feature_cols = [
            'age', 'gender', 'employment_status', 'monthly_income',
            'loan_amount', 'loan_term_months', 'credit_history', 'existing_debts'
        ]

    def load_data(self, dataframe):
        """Loads data into the predictor instance."""
        self.df = dataframe.copy()
        print("[OK] Dataset loaded successfully.")

    def preprocess(self):
        """Handles missing values and encodes categorical variables."""
        # Handle Missing Values (Impute numerical column with median)
        if self.df['monthly_income'].isnull().sum() > 0:
            median_income = self.df['monthly_income'].median()
            self.df['monthly_income'] = self.df['monthly_income'].fillna(median_income)
            print(f"[OK] Missing values in 'monthly_income' imputed with median (KSh {median_income:,.2f}).")

        # Encode Categorical Variables
        categorical_cols = ['gender', 'employment_status', 'credit_history', 'default']
        for col in categorical_cols:
            le = LabelEncoder()
            self.df[col] = le.fit_transform(self.df[col].astype(str))
            self.label_encoders[col] = le
        print("[OK] Categorical features encoded successfully.")

        # Split features and target
        self.X = self.df[self.feature_cols]
        self.y = self.df['default']

    def perform_feature_analysis(self):
        """Computes correlation matrix and saves a Heatmap visualisation."""
        print("\n--- Performing Feature Analysis ---")
        # Include numeric conversion verification
        corr = self.df.drop(columns=['applicant_id']).corr()

        plt.figure(figsize=(10, 8))
        # Custom manual heatmap matrix styling for basic matplotlib compliance
        plt.imshow(corr, cmap='coolwarm', interpolation='nearest')
        plt.colorbar(label='Correlation Coefficient')
        tick_marks = [i for i in range(len(corr.columns))]
        plt.xticks(tick_marks, corr.columns, rotation=45, ha='right')
        plt.yticks(tick_marks, corr.columns)

        # Write values inside cells
        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="black")

        plt.title('Feature Correlation Matrix Heatmap')
        plt.tight_layout()
        plt.savefig('feature_correlation_heatmap.png')
        plt.close()
        print("[OK] Saved Visualisation 1: 'feature_correlation_heatmap.png'")

    def train(self, model_type='KNN'):
        """Trains models and applies cross-validation/hyperparameter tuning for KNN."""
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.25, random_state=42, stratify=self.y
        )

        # Scaling numerical metrics
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        if model_type == 'KNN':
            print("\nTuning hyperparameters for KNN...")
            knn = KNeighborsClassifier()
            param_grid = {'n_neighbors': [3, 5, 7, 9, 11, 15]}
            grid = GridSearchCV(knn, param_grid, cv=5, scoring='accuracy')
            grid.fit(X_train_scaled, y_train)

            self.models['KNN'] = grid.best_estimator_
            print(f"[OK] Best KNN Parameters Found: {grid.best_params_}")

            # Generate Visualisation 2: Hyperparameter tuning performance curve
            plt.figure()
            plt.plot(param_grid['n_neighbors'], grid.cv_results_['mean_test_score'], marker='o', color='purple')
            plt.title('KNN Cross-Validation Accuracy vs K value')
            plt.xlabel('Number of Neighbors (K)')
            plt.ylabel('CV Mean Accuracy')
            plt.grid(True)
            plt.savefig('knn_tuning_curve.png')
            plt.close()
            print("[OK] Saved Visualisation 2: 'knn_tuning_curve.png'")

        elif model_type == 'NaiveBayes':
            self.models['NaiveBayes'].fit(X_train_scaled, y_train)
            print("[OK] Naïve Bayes Classifier trained successfully.")

    def evaluate(self):
        """Generates performance comparison reports and visualisations."""
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.25, random_state=42, stratify=self.y
        )
        X_test_scaled = self.scaler.transform(X_test)

        results = {}

        for name, model in self.models.items():
            if model is not None:
                preds = model.predict(X_test_scaled)
                acc = accuracy_score(y_test, preds)
                report = classification_report(y_test, preds, output_dict=True)
                cm = confusion_matrix(y_test, preds)
                results[name] = {'accuracy': acc, 'report': report, 'cm': cm}

        # Display Structured Performance Summary Table
        print("\n" + "="*50)
        print(f"{'MODEL PERFORMANCE COMPARISON SUMMARY':^50}")
        print("="*50)
        print(f"{'Classifier':<15} | {'Accuracy':<10} | {'Precision (Default)':<20} | {'Recall (Default)':<15}")
        print("-"*50)
        for name, metrics in results.items():
            # '1' corresponds to 'Yes' / Defaulter status
            prec_default = metrics['report']['1']['precision']
            rec_default = metrics['report']['1']['recall']
            print(f"{name:<15} | {metrics['accuracy']:<10.2%} | {prec_default:<20.2%} | {rec_default:<15.2%}")
        print("="*50)

        # Visualisation 3: Model Accuracy Bar Chart Comparison
        plt.figure()
        model_names = list(results.keys())
        accuracies = [results[m]['accuracy'] for m in model_names]
        plt.bar(model_names, accuracies, color=['teal', 'coral'], width=0.4)
        plt.ylim(0, 1.0)
        plt.title('Classifier Test Accuracy Comparison')
        plt.ylabel('Accuracy')
        for i, v in enumerate(accuracies):
            plt.text(i, v + 0.02, f"{v:.2%}", ha='center', fontweight='bold')
        plt.savefig('model_accuracy_comparison.png')
        plt.close()
        print("[OK] Saved Visualisation 3: 'model_accuracy_comparison.png'")

        # Visualisation 4: Confusion Matrix Multi-plot Setup
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for idx, (name, metrics) in enumerate(results.items()):
            ax = axes[idx]
            ax.imshow(metrics['cm'], cmap='Blues', interpolation='nearest')
            ax.set_title(f'{name} Confusion Matrix')
            tick_marks = np.arange(2)
            ax.set_xticks(tick_marks)
            ax.set_yticks(tick_marks)
            ax.set_xticklabels(['No Default', 'Default'])
            ax.set_yticklabels(['No Default', 'Default'])

            # Label figures internally
            thresh = metrics['cm'].max() / 2.
            for i in range(2):
                for j in range(2):
                    ax.text(j, i, format(metrics['cm'][i, j], 'd'),
                            ha="center", va="center",
                            color="white" if metrics['cm'][i, j] > thresh else "black")
            ax.set_ylabel('True Label')
            ax.set_xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('confusion_matrices.png')
        plt.close()
        print("[OK] Saved Visualisation 4: 'confusion_matrices.png'")

    def predict_applicant(self, input_dict):
        """Predicts risk assessment profile for an interactive instance entry."""
        # Clean processing dictionary pipeline matching the feature profile setup
        temp_df = pd.DataFrame([input_dict])

        # Encode inputs based on historical fitting mappings
        for col in ['gender', 'employment_status', 'credit_history']:
            le = self.label_encoders[col]
            # Protection validation if edge values are parsed
            if temp_df[col].iloc[0] not in le.classes_:
                temp_df[col] = le.transform([le.classes_[0]])
            else:
                temp_df[col] = le.transform(temp_df[col])

        # Structural conversion verification matching primary models profile
        processed_input = temp_df[self.feature_cols]
        scaled_input = self.scaler.transform(processed_input)

        # Fetch consensus weights or choose best model profile (KNN selected)
        prediction = self.models['KNN'].predict(scaled_input)[0]
        probabilities = self.models['KNN'].predict_proba(scaled_input)[0]

        # Logic allocation setup tracking risk index categories (Low, Medium, High)
        default_probability = probabilities[1]

        if default_probability < 0.30:
            rating = "Low"
        elif default_probability < 0.65:
            rating = "Medium"
        else:
            rating = "High"

        return rating, default_probability


# ==========================================
# 3. INTERACTIVE BANK OFFICER INTERFACE
# ==========================================
def run_bank_officer_interface(predictor_model):
    print("\n" + "="*50)
    print(f"{'KENYAN BANKING SYSTEM: RISK PREDICTOR CONSOLE':^50}")
    print("="*50)

    while True:
        try:
            print("\nEnter Applicant Data Profile details below (or type 'exit' to quit):")

            age_input = input("1. Applicant Age: ")
            if age_input.lower() == 'exit': break
            age = int(age_input)

            gender = input("2. Gender (M/F): ").strip().upper()
            while gender not in ['M', 'F']:
                gender = input("Invalid option. Please enter M or F: ").strip().upper()

            print("3. Employment Status Options: [1] Employed  [2] Self-Employed  [3] Unemployed")
            emp_choice = input("Select choice (1-3): ").strip()
            emp_map = {'1': 'Employed', '2': 'Self-Employed', '3': 'Unemployed'}
            while emp_choice not in emp_map:
                emp_choice = input("Select a valid index option (1-3): ").strip()
            employment_status = emp_map[emp_choice]

            monthly_income = float(input("4. Monthly Income (KSh): "))
            loan_amount = float(input("5. Requested Loan Amount (KSh): "))
            loan_term_months = int(input("6. Loan Term Period (in Months): "))

            print("7. Credit History Status Options: [1] Good Status  [2] Poor Status History")
            ch_choice = input("Select choice (1-2): ").strip()
            ch_map = {'1': 'Good', '2': 'Poor'}
            while ch_choice not in ch_map:
                ch_choice = input("Select a valid index option (1-2): ").strip()
            credit_history = ch_map[ch_choice]

            existing_debts = float(input("8. Total Outstanding Debt Portfolio Size (KSh): "))

            # Pack details into prediction mapping format
            applicant_data = {
                'age': age,
                'gender': gender,
                'employment_status': employment_status,
                'monthly_income': monthly_income,
                'loan_amount': loan_amount,
                'loan_term_months': loan_term_months,
                'credit_history': credit_history,
                'existing_debts': existing_debts
            }

            # Predict
            risk_rating, risk_prob = predictor_model.predict_applicant(applicant_data)

            print("\n" + "-"*40)
            print(f" PROCESSING RISK CRITERIA ANALYSIS MATRIX...")
            print(f" -> Computed Default Probability Rate: {risk_prob:.2%}")
            print(f" -> Final Assigned Risk Class Rating:  [{risk_rating.upper()}]")
            print("-"*40)

        except ValueError:
            print("\n[!] Input parsing anomaly encountered. Please ensure numerical configurations are applied appropriately.")
        except KeyboardInterrupt:
            break

    print("\nExiting Terminal Dashboard Systems Engine. Goodbye.")


# ==========================================
# 4. EXECUTION PIPELINE MAIN ENGINE
# ==========================================
if __name__ == "__main__":
    print("[1] Simulating Kenyan Financial Credit Approval Data Records...")
    raw_dataset = generate_synthetic_data(num_records=200)

    print("\n[2] Instantiating OOP Class Structure Context Block Pipeline...")
    predictor = LoanRiskPredictor()

    # Load and Data Pipeline Preprocessing
    predictor.load_data(raw_dataset)
    predictor.preprocess()

    # Run structural Matrix analysis checks
    predictor.perform_feature_analysis()

    # Training configurations
    predictor.train(model_type='KNN')
    predictor.train(model_type='NaiveBayes')

    # Evaluation execution run
    predictor.evaluate()

    # Trigger Terminal Interactive Portal interface simulation loop
    run_bank_officer_interface(predictor)