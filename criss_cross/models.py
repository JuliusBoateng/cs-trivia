from django.db import models
from django.core.exceptions import ValidationError
from unicodedata import normalize
from re import sub
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=16, unique=True)

    class Meta:
        ordering = ["name"]

class Board(models.Model):
    MIN_ROWS, MAX_ROWS = 5, 21
    DEFAULT_ROWS = 15

    rows = models.PositiveIntegerField(
        default=DEFAULT_ROWS,
        validators=[
            MinValueValidator(MIN_ROWS),
            MaxValueValidator(MAX_ROWS)
            ]
        )
    
    cols = models.PositiveIntegerField(
        default=DEFAULT_ROWS,
        validators=[
            MinValueValidator(MIN_ROWS),
            MaxValueValidator(MAX_ROWS)
            ]
        )
    
    categories = models.ManyToManyField(Category, related_name="Boards")
    
    def clean(self):
        if self.rows != self.cols:
            raise ValidationError({"rows:" f"rows: {self.rows} and cols: {self.cols} must match"})
        
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cols=models.F("rows")),
                name="board_symmetry"
            )
        ]

'''
Questions/Answers for puzzles
'''
class Clue(models.Model):
    question = models.CharField(max_length=150)
    answer_raw = models.CharField(max_length=21)
    answer_normalized = models.CharField(max_length=21)
    answer_length = models.PositiveIntegerField() # derived
    categories = models.ManyToManyField(Category, related_name="Clues")

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

    def _bounds_check(self):
        if self.start_col >= self.board.cols:
            raise ValidationError({"start_col": f"{self.start_col} out of bounds: {self.board.cols}"})

        if self.start_row >= self.board.rows:
            raise ValidationError({"start_row": f"{self.start_row} out of bounds: {self.board.rows}"})

    def _across_direction_check(self):
        if self.direction == "A":
            across = self.start_col + self.clue.answer_length
            
            if across > self.board.cols:
                raise ValidationError({"start_col": f"Across answer placement: {across} out of bounds: {self.board.cols}"})
    
    def _down_direction_check(self):
        if self.direction == "D":
            down = self.start_row + self.clue.answer_length

            if down > self.board.rows:
                raise ValidationError({"start_row": f"Down answer placement: {down} out of bounds: {self.board.rows}"})

    def clean(self):
        self._bounds_check()
        self._across_direction_check()
        self._down_direction_check()

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

    def _bounds_check(self):
        board = self.clue_placement.board

        if self.col_index >= board.cols:
            raise ValidationError({"col_index": f"{self.col_index} out of bounds: {board.cols}"})

        if self.row_index >= board.rows:
            raise ValidationError({"row_index": f"{self.row_index} out of bounds: {board.rows}"})
    
    def _index_check(self):
        clue = self.clue_placement.clue

        if self.answer_index >= clue.answer_length:
            raise ValidationError({"answer_index": f"{self.answer_index} exceeds answer_length: {clue.answer_length}"})

    def _across_direction_check(self):
        placement = self.clue_placement

        if placement.direction == "A":
            if self.row_index != placement.start_row:
                raise ValidationError({"row_index": f"Across {self.row_index} does not match start_row: {placement.start_row}"})
            
            expected_col_index = placement.start_col + self.answer_index
            if self.col_index != expected_col_index:
                raise ValidationError({"col_index": f"Down {self.col_index} does not match expected col_index: {expected_col_index}"})

    def _down_direction_check(self):
        placement = self.clue_placement

        if placement.direction == "D":
            if self.col_index != placement.start_col:
                raise ValidationError({"col_index": f"Down {self.col_index} does not match start_col: {placement.start_col}"})
            
            expected_row_index = placement.start_row + self.answer_index
            if self.row_index != expected_row_index:
                raise ValidationError({"row_index": f"Down {self.row_index} does not match expected row_index: {expected_row_index}"})

    def clean(self):
        self._bounds_check()
        self._index_check()
        self._across_direction_check()
        self._down_direction_check()
