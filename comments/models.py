from django.db import models
from snippets.models import CustomUser,Snippet
from time import timezone
class Comment(models.Model):
    detail=models.CharField(max_length=400)
    snippet=models.ForeignKey(Snippet,on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    parent=models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True)
    date_commented=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return " {} by {} ".format(self.detail,self.user.email)
    
    # def get_absolute_url(self):
    #     return reverse('detail_comments',args=[str(self.pk)])

