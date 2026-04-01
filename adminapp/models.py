from django.db import models

# Create your models here.
class datasetModel(models.Model):
    data_id = models.AutoField(primary_key=True)
    dataset = models.FileField(upload_to='media/dataset/')
    date_time = models.DateTimeField(auto_now=True)
   # Add these fields

    xgb_accuracy = models.FloatField(null=True)
    xgb_precision = models.FloatField(null=True)
    xgb_recall = models.FloatField(null=True)
    xgb_f1_score = models.FloatField(null=True)

    cat_accuracy = models.FloatField(null=True)
    cat_precision = models.FloatField(null=True)
    cat_recall = models.FloatField(null=True)
    cat_f1_score = models.FloatField(null=True)
    lr_accuracy = models.FloatField(null=True)
    lr_precision = models.FloatField(null=True)
    lr_recall = models.FloatField(null=True)
    lr_f1_score = models.FloatField(null=True)
    lr_algo = models.CharField(max_length=500,null=True)
    class Meta:
        db_table = 'Upload Dataset'

# class Predict(models.Model):
#     predict_id = models.AutoField(primary_key = True)
#     type = models.CharField(max_length=100)
#     amount = models.FloatField(null = True)
#     oldbalanceOrg = models.FloatField(null = True)
#     newbalanceOrig = models.FloatField(null = True)
#     oldbalanceDest = models.FloatField(null = True)
#     newbalanceDest = models.FloatField(null = True)
#     result = models.CharField(max_length=100)
#     class Meta:
#         db_table = 'Predict Form Data'

from django.db import models

class Predict(models.Model):
    predict_id = models.AutoField(primary_key=True)

    # 🔹 Input Features
    step = models.IntegerField(default=1)  # optional time step
    type = models.CharField(max_length=50)

    amount = models.FloatField(null=True)
    oldbalanceOrg = models.FloatField(null=True)
    newbalanceOrig = models.FloatField(null=True)
    oldbalanceDest = models.FloatField(null=True)
    newbalanceDest = models.FloatField(null=True)

    # 🔹 Engineered Features (for traceability)
    balance_diff_org = models.FloatField(null=True, blank=True)
    balance_diff_dest = models.FloatField(null=True, blank=True)
    zero_balance_flag = models.IntegerField(null=True, blank=True)

    # 🔹 Prediction Output
    fraud_probability = models.FloatField(null=True, blank=True)
    result = models.CharField(max_length=20)  # Fraud / Genuine

    # 🔹 Timestamp (VERY IMPORTANT for real-time systems)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'predict_form_data'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type} | {self.amount} | {self.result}"