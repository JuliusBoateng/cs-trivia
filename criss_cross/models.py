from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Board(models.Model):
    rows = models.PositiveIntegerField()
    cols = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rows__gte=5) & models.Q(rows__lte=21),
                name="board_rows_range"),
            models.CheckConstraint(
                condition=models.Q(cols__gte=5) & models.Q(cols__lte=21),
                name="board_cols_range"
            ),
            models.CheckConstraint(
                condition=models.Q(cols=models.F("rows")),
                name="board_row_col_symmetry"
            )
        ]

'''
Physical squares on the board
'''
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
        if self.col_index >= self.board.cols:
            raise ValidationError("Col Index out of bounds")

        if self.row_index >= self.board.rows:
            raise ValidationError("Row Index out of bounds")

'''
Questions/Answers for puzzle
'''
class Clue(models.Model):
    question = models.CharField(max_length=150)
    answer = models.CharField(max_length=21)
    length = models.PositiveIntegerField() # derived

    def save(self, *args, **kwargs):
        self.length = len(self.answer)
        super().save(*args, **kwargs)

'''
Mapping between board and clue
'''
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
                name="clue_placement_unique_row_col_direction"),
            models.UniqueConstraint(
                fields=["board", "clue"],
                name="clue_placement_unique_board_clue"
            )
        ]
    
    def clean(self):
        if self.start_col >= self.board.cols:
            raise ValidationError("start_col out of bounds")

        if self.start_row >= self.board.rows:
            raise ValidationError("start_row out of bounds")

        if self.direction == "A":
            if self.start_col + self.clue.length > self.board.cols:
                raise ValidationError("Across clue overflows board")

        if self.direction == "D":
            if self.start_row + self.clue.length > self.board.rows:
                raise ValidationError("Down clue overflows board")


'''
Mapping of answer to physical cells on the board
'''
class ClueCell(models.Model):
    clue_placement = models.ForeignKey(CluePlacement, on_delete=models.CASCADE)
    board_cell = models.ForeignKey(BoardCell, on_delete=models.CASCADE)
    answer_index = models.PositiveIntegerField()

    # It's fine for placements to appear on multiple cells.
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["clue_placement", "board_cell"],
                name="clue_cell_unique_cell_per_placement"
            ), # placements must only have one index for a specific cell
            models.UniqueConstraint(
                fields=["clue_placement", "answer_index"],
                name="clue_cell_unique_index_per_placement"
            ), # prevents the same index to mapping to different cells on the board
        ]

    def clean(self):
        if self.board_cell.board_id != self.clue_placement.board_id:
            raise ValidationError("Cell must belong to same board")