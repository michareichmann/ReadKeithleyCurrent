import ROOT
import array

xx1 = []
yy1 = []
for i in range(-10, 11):
    xx1.append(i)
    yy1.append(i * i)

xx2 = []
yy2 = []
for i in range(-20, 21):
    xx2.append(i)
    yy2.append(i * i * i)

x1 = array.array('d', xx1)
y1 = array.array('d', yy1)
x2 = array.array('d', xx2)
y2 = array.array('d', yy2)

g1 = ROOT.TGraph(len(x1), x1, y1)
g1.SetMarkerColor(1)
g1.SetMarkerStyle(21)

g2 = ROOT.TGraph(len(x2), x2, y2)
g2.SetMarkerColor(2)
g2.SetMarkerStyle(20)
g2.SetName("g2")

c1 = ROOT.TCanvas("c1", "PadTest", 500, 500)
p1 = ROOT.TPad("p1", "", 0, 0, 1, 1)
p1.SetFillColor(40)
p1.SetGrid()
p1.Draw()
p1.cd()

hr = c1.DrawFrame(min(xx1), min(yy1), max(xx1), max(yy1))
hr.SetXTitle("X title")
hr.SetYTitle("Y title")
p1.GetFrame().SetFillColor(21)
p1.GetFrame().SetBorderSize(12)

g1.Draw("LP")


p2 = ROOT.TPad("p2", "", 0, 0, 1, 1)

p2.SetFillStyle(4000)
p2.SetFillColor(0)
p2.SetFrameFillStyle(4000)
p2.Draw()
p2.cd()

hframe = p2.DrawFrame(min(xx2), min(yy2), max(xx2), max(yy2))
hframe.GetXaxis().SetTickLength(0)
hframe.GetYaxis().SetTickLength(0)
hframe.GetXaxis().SetLabelOffset(99)
hframe.GetYaxis().SetLabelOffset(99)
g2.Draw("LP")

axis = ROOT.TGaxis(max(xx2), min(yy2), max(xx2), max(yy2),min(yy2),max(yy2),510,"+L")
axis.SetLabelSize(0.035)
axis.SetLineColor(2)
axis.SetLabelColor(2)
axis.SetLabelOffset(0.01)
axis.Draw()

c1.Update()

# p1.SetFillStyle(4000)
# p2.SetFillStyle(4000)
# p2.SetFillColor(0)
#
# p1.Draw()
# p1.cd()
# g1.Draw("AC")
#
# c1.cd()
#
# p2.Draw()
# p2.cd()
# g2.Draw("AC")

raw_input()
