__author__ = 'micha'

# ====================================
# IMPORTS
# ====================================
from ROOT import TH1F, TH1, TCanvas

# ====================================
# ROOT CLASS
# ====================================
class Analysis:
    def __init__(self, infos, run_mode, number):
        self.number = (True if number == "1" else False)
        self.runmode = run_mode
        self.infos = infos
        # histogram of distribution
        self.c1 = TCanvas("c1", 'histo', 800, 400)
        self.h1 = {}
        self.make_histos()

    def main_loop(self):
        for key in self.infos.keithleys:
            self.h1[key].Draw()
        self.c1.Update()

    def make_histos(self):
        for key in self.infos.keithleys:
            h1 = TH1F('test', 'test', 100, 0, 0.15)
            # h1.SetBit(TH1.kCanRebin)
            for current in self.infos.current_y[key]:
                h1.Fill(current)
            self.h1[key] = h1