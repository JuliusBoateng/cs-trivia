from django.db import models
from django.core.exceptions import ValidationError
from unicodedata import normalize
from re import sub

# Create your models here.
class Board(models.Model):
    rows = models.PositiveIntegerField()
    cols = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rows__gte=5) & models.Q(rows__lte=21),
                name="board_rows_range"
            ),
            models.CheckConstraint(
                condition=models.Q(cols__gte=5) & models.Q(cols__lte=21),
                name="board_cols_range"
            ),
            models.CheckConstraint(
                condition=models.Q(cols=models.F("rows")),
                name="board_symmetry"
            )
        ]

class Category(models.Model):
    name = models.CharField(max_length=16, unique=True)

    class Meta:
        ordering = ["name"]

'''
Questions/Answers for puzzles
'''
class Clue(models.Model):
    question = models.CharField(max_length=150)
    answer_raw = models.CharField(max_length=21)
    answer_normalized = models.CharField(max_length=21)
    answer_length = models.PositiveIntegerField() # derived
    categories = models.ManyToManyField(Category)

    @staticmethod
    def _normalize_answer(s):
        s = normalize("NFKD", s) # separates accents from chars
        s = s.encode("ascii", "ignore").decode() # removes accents
        s = sub(r"[^A-Z0-9]", "", s.upper()) # replace non-alphanumeric chars
        return s

    def save(self, *args, **kwargs):
        self.answer_raw = self.answer_raw.strip()
        self.answer_normalized = self._normalize_answer(self.answer_raw)
        self.answer_length = len(self.answer_normalized)
        super().save(*args, **kwargs)

'''
Mapping between Board and Clue
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
            raise ValidationError(f"start_col: {self.start_col} out of bounds: {self.board.cols}")

        if self.start_row >= self.board.rows:
            raise ValidationError(f"start_row: {self.start_row} out of bounds: {self.board.rows}")

        if self.direction == "A":
            if self.start_col + self.clue.answer_length > self.board.cols:
                raise ValidationError(f"Across answer out of bounds: {self.start_col + self.clue.answer_length} expected: {self.board.cols}")

        if self.direction == "D":
            if self.start_row + self.clue.answer_length > self.board.rows:
                raise ValidationError(f"Down answer out of bounds: {self.start_row + self.clue.answer_length } expected: {self.board.rows}")

'''
Mapping between CluePlacement and Board cells
'''
class ClueCell(models.Model):
    clue_placement = models.ForeignKey(CluePlacement, on_delete=models.CASCADE)
    row_index = models.PositiveIntegerField()
    col_index = models.PositiveIntegerField()
    answer_index = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["clue_placement", "row_index", "col_index"],
                name='clue_cell_unique_placement_row_col'
            ),
            models.UniqueConstraint(
                fields=["clue_placement", "answer_index"],
                name="clue_cell_unique_index_per_placement"
            ),
        ]

    def clean(self):
        placement = self.clue_placement
        board = placement.board
        clue = placement.clue

        if self.col_index >= board.cols:
            raise ValidationError(f"col_index: {self.col_index} out of bounds: {board.cols}")

        if self.row_index >= board.rows:
            raise ValidationError(f"row_index: {self.row_index} out of bounds: {board.rows}")
        
        if self.answer_index >= clue.answer_length:
            raise ValidationError(f"answer_index: {self.answer_index} exceeds answer_length: {clue.answer_length}")

        if placement.direction == "A":
            if self.row_index != placement.start_row:
                raise ValidationError(f"Across row_index: {self.row_index} does not match start_row: {placement.start_row}")
            
            expected_col_index = placement.start_col + self.answer_index
            if self.col_index != expected_col_index:
                raise ValidationError(f"Across col_index: {self.col_index} does not match expected col_index: {expected_col_index}")

        if placement.direction == "D":
            if self.col_index != placement.start_col:
                raise ValidationError(f"Down col_index: {self.col_index} does not match start_col: {placement.start_col}")
            
            expected_row_index = placement.start_row + self.answer_index
            if self.row_index != expected_row_index:
                raise ValidationError(f"Down row_index: {self.row_index} does not match expected row_index: {expected_row_index}")
