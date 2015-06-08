import ROOT
import array


marker_size = 0.5
pad_color = 26

# first graph for the current
def graph1(key, xx, current):
    x = array.array('d', xx[key])
    y = array.array('d', current[key])
    g1 = ROOT.TGraph(len(x), x, y)
    g1.SetMarkerColor(2)
    g1.SetMarkerSize(marker_size)
    g1.SetMarkerStyle(20)
    return g1

# second graph for the voltage
def graph2(key, xx, voltage):
    x = array.array('d', xx[key])
    y = array.array('d', voltage[key])
    g2 = ROOT.TGraph(len(x), x, y)
    g2.SetMarkerColor(4)
    g2.SetMarkerSize(marker_size)
    g2.SetMarkerStyle(20)
    return g2


# draw the axis on the right side
def axis1(key, xx, dx):
    a1 = ROOT.TGaxis(max(xx[key]) + dx, -1100, max(xx[key]) + dx, 1100, -1100, 1100, 510, "+L")
    a1.SetTitle("#font[22]{voltage [V]}")
    a1.SetTitleSize(0.06)
    a1.SetTitleOffset(0.5)
    a1.CenterTitle()
    a1.SetTitleColor(4)
    a1.SetLabelSize(0.05)
    a1.SetLineColor(4)
    a1.SetLabelColor(4)
    a1.SetLabelOffset(0.01)
    a1.Draw()
    return a1


# pad 1 for first graph (main pad)
def pad1(key):
    p1 = ROOT.TPad("p1_" + key, "", 0, 0, 1, 1)
    p1.SetFillColor(pad_color)
    p1.SetBorderSize(4)
    p1.SetBorderMode(1)
    p1.SetGridx()
    p1.Draw()
    p1.cd()

    return p1

# frame for pad 1
def frame1(canvas, key, xx, current, dx, dy ):
    h1 = canvas.DrawFrame(min(xx[key]) - dx, min(current[key]) - dy, max(xx[key]) + dx, max(current[key]) + dy)
    # X-axis
    h1.GetXaxis().SetTitle("#font[22]{time [hh:mm]}")
    h1.GetXaxis().CenterTitle()
    h1.GetXaxis().SetTimeFormat("%H:%M")
    h1.GetXaxis().SetTimeOffset(1486249200)
    h1.GetXaxis().SetTimeDisplay(1)
    h1.GetXaxis().SetLabelSize(0.05)
    h1.GetXaxis().SetTitleSize(0.06)
    h1.GetXaxis().SetTitleOffset(0.9)
    h1.SetTitleSize(0.05)
    # Y-axis
    h1.GetYaxis().SetTitleOffset(0.69)
    h1.GetYaxis().SetTitle("#font[22]{current [nA]}")
    h1.GetYaxis().CenterTitle()
    h1.GetYaxis().SetLabelSize(0.05)
    h1.GetYaxis().SetTitleSize(0.06)
    h1.GetYaxis().SetTitleOffset(0.7)
    return h1

# pad 2 for second graph (transparent)
def pad2(key):
    p2 = ROOT.TPad("p2_" + key, "", 0, 0, 1, 1)
    p2.SetFillStyle(4000)
    p2.SetFillColor(0)
    p2.SetFrameFillStyle(4000)
    p2.SetGridy()
    p2.Draw()
    p2.cd()
    return p2

# frame 2 for pad 2
def frame2(key, xx, dx, pad):
    h2 = pad.DrawFrame(min(xx[key]) - dx, -1100, max(xx[key]) + dx, 1100)
    h2.GetXaxis().SetTickLength(0)
    h2.GetYaxis().SetTickLength(0)
    h2.GetXaxis().SetLabelOffset(99)
    h2.GetYaxis().SetLabelOffset(99)
    return h2

# pad 3 for titles (transparent)
def pad3(key):
    p3 = ROOT.TPad("p3_" + key, "", 0, 0, 1, 1)
    p3.SetFillStyle(4000)
    p3.SetFillColor(0)
    p3.SetFrameFillStyle(4000)
    p3.Draw()
    p3.cd()
    return p3

# text 1
def text1(value):
    t1 = ROOT.TText(0.1, 0.92, value)
    t1.SetTextSize(0.09)
    t1.Draw()
    return t1
