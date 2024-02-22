import board
from kmk.kmk_keyboard import KMKKeyboard as _KMKKeyboard
from kmk.scanners import DiodeOrientation
from kmk.scanners.keypad import KeysScanner
from kmk.scanners.keypad import MatrixScanner

class KMKKeyboard(_KMKKeyboard):
    def __init__(self):

        self.col_pins = (
            board.GP21,
            board.GP20,
            board.GP19,
            board.GP18,
        )
        self.row_pins = (
            board.GP11,
            board.GP12,
            board.GP13,
            board.GP14,
            board.GP15,
        )

        # create and register the scanner
        self.matrix = [
            MatrixScanner(
            column_pins=self.col_pins,
            row_pins=self.row_pins,
            columns_to_anodes=DiodeOrientation.COL2ROW,
            interval=0.02,
            max_events=64
            ),
            KeysScanner(
            # pins=[board.GP6, board.GP27, board.GP26], # 通常はこれ
            pins=[board.GP27, board.GP26], ## 230823  ## スリープモードの実験用
            value_when_pressed=False,
            pull=True,
            interval=0.02,
            max_events=64
            ),
            ]
        
        self.coord_mapping = [
            0,  1,  2,  3,
            4,  5,  6,  7,
            8,  9,  10, 11,
            12, 13, 14, 15,
            16, 17, 18,
            19, 20, 21,
            ]
