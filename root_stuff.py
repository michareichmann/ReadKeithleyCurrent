# ====================================
# IMPORTS
# ====================================
from ROOT import TCanvas, TPad, TGaxis, TText, TGraph, TBox, TPaveText, gStyle, TH1F, TH1
import array
import functions
import os

# infos=KeithleyInfo("df", "df", "df", "df")

# ====================================
# CONSTANTS
# ====================================
marker_size = 0.5
pad_color = 0  # was 26
axis_title_size = 0.07
left_margin = 0.08

space = 0.015
title = 0.93


# ====================================
# HELPER FUNCTIONS
# ====================================
def make_transparent(pad):
    pad.SetFillStyle(4000)
    pad.SetFillColor(0)
    pad.SetFrameFillStyle(4000)


def write_run(run):
    if int(run) < 10:
        run = "00" + str(run)
    elif int(run) < 100:
        run = "0" + str(run)
    return str(run)


# ====================================
# ROOT CLASS
# ====================================
class RootGraphs:
    def __init__(self, infos, run_mode, number):
        self.number = (True if number == "1" else False)
        self.runmode = run_mode
        self.infos = infos
        if self.infos.single_mode:
            self.c = TCanvas("c", self.canvas_name(), 1500, 1000)
        else:
            self.c = TCanvas("c", self.canvas_name(), 1000, 1000)
        # dividing canvas into pads
        self.p5 = TPad("p5", "", space, space, 1 - space, title / 3 - space / 2)
        self.p6 = TPad("p6", "", space, title / 3 + space / 2, 1 - space, title * 2 / 3 - space / 2)
        self.p7 = TPad("p7", "", space, title * 2 / 3 + space / 2, 1 - space, title - space / 2)
        if number == "1":
            self.p7 = TPad("p7", "", space, space, 1 - space, title - space / 2)
        self.p8 = TPad("p8", "", 0, title, 1, 1)
        self.draw_pads()
        # title texts
        self.t2 = TPaveText(0, 0, 1, 0.7, "NB")
        self.t3 = TPaveText(0.5, 0, 1, 0.7, "NB")
        self.draw_titles()
        # graphs
        self.g1 = {}
        self.g2 = {}
        self.make_graphs()
        # graph pads
        self.p1 = {}
        self.p2 = {}
        self.p3 = {}
        self.make_pads()
        # margins
        self.ymin = {}
        self.xmin = {}
        self.ymax = {}
        self.xmax = {}
        self.make_margins()
        # second axis
        self.a1 = {}
        self.make_axis()
        # box
        self.b1 = self.make_box()
        # pad titles
        self.t1 = {}
        self.make_pad_title()
        # run lines
        self.run_lines = []
        
    def print_loop(self):
        self.make_graphs()
        self.make_pads()
        self.make_margins()
        ind = 0
        for key in self.infos.keithleys:
            self.goto_pad(ind)
            ind += 1
            self.p1[key].cd()
            self.draw_frame1(key)
            self.g2[key].Draw("P")
            self.p2[key].cd()
            self.draw_frame2(key)
            self.g1[key].Draw("P")
        self.c.Update()
            
    def main_loop(self):
        ind = 0
        for key in self.infos.keithleys:
            self.goto_pad(ind)
            # first pad with voltage, frame and second axis
            self.p1[key].Draw()
            self.p1[key].cd()
            self.draw_frame1(key)
            self.g2[key].Draw("P")
            self.a1[key].Draw()
            # second pad with pad titles and box
            self.p3[key].Draw()
            self.p3[key].cd()
            self.b1.Draw("L")
            self.t1[key].Draw()
            # third pad with current, frame and run lines
            self.p2[key].Draw()
            self.p2[key].cd()
            self.draw_frame2(key)
            if not self.runmode and not self.infos.single_mode:
                self.make_lines(key)
            self.g1[key].Draw("P")
            ind += 1
        self.c.Update()

    def goto_pad(self, index):
        if index == 0:
            self.p7.cd()
        elif index == 1:
            self.p6.cd()
        elif index == 2:
            self.p5.cd()

    def make_lines(self, key):
        for i in range(int(self.infos.run_start), int(self.infos.run_stop) + 1):
            # run start
            ymin = self.ymin[key]
            ymax = self.ymax[key]
            start = functions.convert_time(self.infos.get_time(i, "start time"))
            a2 = TGaxis(start, ymin, start, ymax, ymin, ymax, 510, "+SU")
            tit = "run " + str(i) + "  "
            a2.SetLineColor(1)
            a2.SetTickSize(0)
            a2.SetLabelSize(0)
            a2.SetTitleSize(0.05)
            a2.SetTitleOffset(0.1)
            if self.infos.single_mode:
                a2.SetTitleSize(0.025)
                a2.SetTitleOffset(0.25)
                flux = str(self.infos.data[functions.convert_run(i)]["measured flux"])
                spaces = ""
                for j in range(5 - len(flux)):
                    spaces += " "
                tit = "flux " + flux + spaces
            a2.SetTitle(tit)
            # run stop
            stop = functions.convert_time(self.infos.get_time(i, "stop time"))
            a3 = TGaxis(stop, ymin, stop, ymax, ymin, ymax, 510, "-SU")
            a3.SetLineColor(13)
            a3.SetTickSize(0)
            a3.SetLabelSize(0)
            # draw only for runs longer than 4 minutes
            if stop - start > 20 * 60:
                a2.Draw()
                a3.Draw()
            self.c.Update()
            self.run_lines.append(a2)
            self.run_lines.append(a3)

    def make_pad_title(self):
        for key, value in self.infos.keithleys.items():
            t1 = TText(0.08, 0.88, value)
            t1.SetTextSize(0.09)
            if self.infos.single_mode:
                t1.SetTextSize(0.07)
            self.t1[key] = t1

    @staticmethod
    def make_box():
        b1 = TBox(0, 0, 1, 1)
        b1.SetLineWidth(3)
        b1.SetFillStyle(4000)
        # b1.Draw("L")
        return b1

    def make_axis(self):
        for key in self.infos.keithleys:
            a1 = TGaxis(self.xmax[key], -1100, self.xmax[key], 1100, -1100, 1100, 510, "+L")
            a1.SetTitle("#font[22]{voltage [V]}")
            a1.SetTitleSize(axis_title_size)
            a1.SetTitleOffset(0.46)
            a1.CenterTitle()
            a1.SetTitleColor(4)
            a1.SetLabelSize(0.05)
            if self.number:
                a1.SetLabelSize(0.025)
                a1.SetTitleSize(0.05)
                a1.SetTitleOffset(0.6)
            a1.SetLineColor(4)
            a1.SetLabelColor(4)
            a1.SetLabelOffset(0.01)
            self.a1[key] = a1

    def make_margins(self):
        for key in self.infos.keithleys:
            dx = 0.05 * (max(self.infos.time_x[key]) - min(self.infos.time_x[key]))
            dy = 0.1 * (max(self.infos.current_y[key]) - min(self.infos.current_y[key]))
            self.ymin[key] = min(self.infos.current_y[key]) - dy
            self.ymax[key] = max(self.infos.current_y[key]) + dy
            if len(self.infos.current_y[key]) < 2:
                self.ymin[key] = 0
                self.ymax[key] = 1
            self.xmin[key] = min(self.infos.time_x[key]) - dx
            self.xmax[key] = max(self.infos.time_x[key]) + dx

    def canvas_name(self):
        canvas_name = "Keithley Currents for Run " + str(self.infos.run_start)
        if not self.runmode:
            canvas_name = "Keithley Currents from " + str(self.infos.run_start) + " to " + str(self.infos.run_stop)
        return canvas_name

    def set_canvas(self, color):
        self.c.SetFillColor(color)  # was 17

    def draw_pads(self):
        self.p5.Draw()
        self.p6.Draw()
        self.p7.Draw()
        self.p8.Draw()

    def draw_titles(self):
        self.p8.cd()
        sig_type = self.infos.type
        if sig_type != "signal" and sig_type != "pedestal" and sig_type != "pedastal":
            sig_type = "unknown"
        title_text1 = 'Overview of all runs of ' + self.infos.dia1 + ' & ' + self.infos.dia2
        title_text2 = ""
        if self.infos.single_mode:
            title_text1 = str(self.infos.start) + " - " + str(self.infos.stop)
            title_text2 = ""
        elif not self.infos.time_mode:
            title_text1 = "PSI" + self.infos.start_run + " - " + sig_type + " run"
            title_text2 = "Flux = " + str(self.infos.flux) + " kHz/cm^{2}"
            if self.infos.flux == -1:
                title_text2 = "Flux not measured"
            middle_run = str((int(self.infos.run_stop) + int(self.infos.run_start)) / 2 + 1)
            if not self.runmode:
                title_text1 = "PSI" + functions.convert_run(self.infos.run_start) + " - " + self.infos.run_stop
                title_text2 = 'all runs of ' + self.infos.get_info(middle_run, "diamond 1") + ' & ' + self.infos.get_info(middle_run, "diamond 2")
        self.t2.AddText(title_text1)
        self.t2.SetAllWith("", "Align", 11)
        self.t2.SetAllWith("", "Size", 0.5)
        self.t2.SetFillColor(0)
        self.t3.AddText(title_text2)
        self.t3.SetAllWith("", "Align", 31)
        self.t3.SetAllWith("", "Size", 0.5)
        self.t3.SetFillColor(0)
        self.t2.Draw()
        if not self.infos.time_mode:
            self.t3.Draw()

    def make_graphs(self):
        for key in self.infos.keithleys:
            x = array.array('d', self.infos.time_x[key])
            # current
            y = array.array('d', self.infos.current_y[key])
            g1 = TGraph(len(x), x, y)
            g1.SetName("current")
            g1.SetMarkerColor(2)
            g1.SetMarkerSize(marker_size)
            g1.SetMarkerStyle(20)
            # voltage
            y = array.array('d', self.infos.voltage_y[key])
            g2 = TGraph(len(x), x, y)
            g2.SetMarkerColor(4)
            g2.SetMarkerSize(marker_size)
            g2.SetMarkerStyle(20)
            self.g1[key] = g1
            self.g2[key] = g2

    def make_pads(self):
        for key in self.infos.keithleys:
            # voltage
            p1 = TPad("p1_" + key, "", 0, 0, 1, 1)
            p1.SetFillColor(pad_color)
            p1.SetGridy()
            p1.SetMargin(left_margin, 0.07, 0.15, 0.15)
            self.p1[key] = p1
            # current
            p2 = TPad("p2_" + key, "", 0, 0, 1, 1)
            p2.SetGridx()
            p2.SetMargin(left_margin, 0.07, 0.15, 0.15)
            make_transparent(p2)
            self.p2[key] = p2
            # pad title + box
            p3 = TPad("p3_" + key, "", 0, 0, 1, 1)
            make_transparent(p3)
            self.p3[key] = p3

    # frame for voltage
    def draw_frame2(self, key):
        h2 = self.p2[key].DrawFrame(self.xmin[key], self.ymin[key], self.xmax[key], self.ymax[key])
        # X-axis
        h2.GetXaxis().SetTitle("#font[22]{time [hh:mm]}")
        h2.GetXaxis().CenterTitle()
        h2.GetXaxis().SetTimeFormat("%H:%M")
        h2.GetXaxis().SetTimeOffset(-3600)
        h2.GetXaxis().SetTimeDisplay(1)
        h2.GetXaxis().SetLabelSize(0.05)
        h2.GetXaxis().SetTitleSize(axis_title_size)
        h2.GetXaxis().SetTitleOffset(0.85)
        # Y-axis
        h2.GetYaxis().SetTitleOffset(0.69)
        h2.GetYaxis().SetTitle("#font[22]{current [nA]}")
        h2.GetYaxis().CenterTitle()
        h2.GetYaxis().SetLabelSize(0.05)
        h2.GetYaxis().SetTitleSize(axis_title_size)
        h2.GetYaxis().SetTitleOffset(0.58)
        if self.infos.single_mode:
            h2.GetXaxis().SetLabelSize(0.025)
            h2.GetYaxis().SetLabelSize(0.025)
            h2.GetXaxis().SetTitleSize(0.05)
            h2.GetYaxis().SetTitleSize(0.05)
            h2.GetXaxis().SetTitleOffset(0.85)
            h2.GetYaxis().SetTitleOffset(0.69)

    # frame for current
    def draw_frame1(self, key):
        h1 = self.p1[key].DrawFrame(self.xmin[key], -1100, self.xmax[key], 1100)
        h1.GetXaxis().SetTickLength(0)
        h1.GetYaxis().SetTickLength(0)
        h1.GetXaxis().SetLabelOffset(99)
        h1.GetYaxis().SetLabelOffset(99)

    # save the root to file
    def save_as(self, formats):
        # check if dir exists
        dirs = os.path.dirname("runs/")
        try:
            os.stat(dirs)
        except OSError:
            os.mkdir(dirs)
        run = 'run' + write_run(self.infos.run_start) + '-' + write_run(self.infos.run_stop)
        if self.infos.time_mode:
            run = 'all_'+self.infos.dia1 + '_' + self.infos.dia2 + '(' + write_run(self.infos.run_start) + '-' + write_run(self.infos.run_stop) + ')'
        elif self.infos.run_stop == '-1':
            run = 'run' + write_run(self.infos.run_start)
        if formats == "all":
            ftypes = [".pdf", ".eps", ".root"]
            for ftype in ftypes:
                filename = "runs/" + str(run) + ftype
                self.c.SaveAs(filename)
        else:
            filename = "runs/" + str(run) + "." + str(formats)
            self.c.SaveAs(filename)
