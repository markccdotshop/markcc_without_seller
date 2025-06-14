from django.db import models

class BIN(models.Model):
    bin_start = models.CharField(max_length=20, unique=True)  # Set as unique
    bin_card_type = models.CharField(max_length=50)
    bin_card_level = models.CharField(max_length=50)
    bin_card_comptype = models.CharField(max_length=50)
    bin_bank_name = models.CharField(max_length=100)
    bin_country_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.bin_start} - {self.bin_card_type} - {self.bin_card_level}"
