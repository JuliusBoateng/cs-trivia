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

class BoardCell(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    row_index = models.PositiveIntegerField()
    col_index = models.PositiveIntegerField()
    value = models.CharField(max_length=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["board", "row_index", "col_index"],
                name='board_cell_unique_board_row_col'
            )
        ]

    def clean(self):
        if self.row_index >= self.board.rows:
            raise ValidationError("Row Index out of bounds")

        if self.col_index >= self.board.cols:
            raise ValidationError("Col Index out of bounds")

class Clue(models.Model):
    question = models.CharField(max_length=150)
    answer = models.CharField(max_length=21)
    length = models.PositiveIntegerField() # derived

class CluePlacement(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    clue = models.ForeignKey(Clue, on_delete=models.CASCADE)
    start_row = models.PositiveIntegerField()
    start_col = models.PositiveIntegerField()

    direction = models.CharField(
        max_length=1,
        choices=[
            ("A", "Across"),
            ("D", "Down"),
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["board", "start_row", "start_col", "direction"],
                name="clue_placement_unique_row_col_direction")
        ]

# Derived from CluePlacement
class ClueCell(models.Model):
    clue_placement = models.ForeignKey(CluePlacement, on_delete=models.CASCADE)
    board_cell = models.ForeignKey(BoardCell, on_delete=models.CASCADE)
    clue_index = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["clue_placement", "clue_index"],
                name="unique_index_per_placement"
            ),
            models.UniqueConstraint(
                fields=["clue_placement", "board_cell"],
                name="unique_cell_per_placement"
            )
        ]