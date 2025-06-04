from django.db import models

# Create your models here.

class TaskLog(models.Model):
    task_name = models.CharField(max_length = 100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        
        return None
    
    class Meta:
        ordering = ['start_time']