from django.db import models


class BoardTemplate(models.Model):
    subject = models.CharField(max_length=60)
    crawling_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Board(BoardTemplate):
    BOARD_FIELDS = (
        ('n', '공지사항'),
        ('p', '가정통신문')
    )
    post_id = models.PositiveIntegerField()
    content = models.TextField()
    school_name = models.CharField(max_length=60)
    category = models.CharField(max_length=40, choices=BOARD_FIELDS)
    post_date = models.DateField()

    class Meta:
        ordering = ('-post_date',)

    def __str__(self):
        return f'{self.school_name} - {self.subject}'


class FileBoard(BoardTemplate):
    post = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='file_board'
    )
    file = models.FileField(upload_to='download_files')

    def __str__(self):
        return f'{self.post.school_name} - {self.subject}'
