
class PosterType:
    def __init__(self):
        self.width=0
        self.height=0
        self.margin=0
        self.cover_size=0
        self.section_margin=0

    def poster_8x10(self):
        self.width=2400
        self.height=3000
        self.margin=150
        self.cover_size=1600
        self.section_margin=15