from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Board(models.Model):
    rows = models.PositiveIntegerField()
    cols = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rows__gte=1) & models.Q(rows__lte=21),
                name="board_rows_range"),
            models.CheckConstraint(
                condition=models.Q(cols__gte=1) & models.Q(cols__lte=21),
                name="board_cols_range"
            )
        ]

class Solution(models.Model):
    question = models.CharField(max_length=150)
    answer = models.CharField(max_length=21)

class BoardCoordinate(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    row_index = models.PositiveIntegerField()
    col_index = models.PositiveIntegerField()
    pk = models.CompositePrimaryKey("board", "row_index", "col_index")
    value = models.CharField(max_length=1)
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)

    def clean(self):
        if self.row_index >= self.board.rows:
            raise ValidationError("Row Index out of bounds")

        if self.col_index >= self.board.cols:
            raise ValidationError("Col Index out of bounds")

# Next map solution to coordinates