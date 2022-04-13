%% Project: MHH Dissertation
%  Title/File: BendStr.m
%  Author: Bruno Luna 
%  Date (start): 23 May 2021
%
%  Content
%  ------------
% 
%  This file contains code for calculation of bending stress on beam
%
%  Main assumptions:
%  1 - Timoshenko ("basic" formulation) conditions met
%  2 - Constant cross section
%  3 - Linear material (Hook law valid)
%

function Sbmax = BendStr(InpData, M)
 
%% Setup the parameters used
% Length of beam (mm)
L = InpData.Len.L;   % Value of lengths for each year considered (mm)
x = InpData.Len.x;   % Points to calculate beam
I = InpData.CS.I;    % Second moment of area (mm^4)
c = InpData.CS.c;    % Distance of most outward fibers from neutral axis (mm)
np = InpData.Gen.np; % Number of points to calculate beam (adim)
Lw = InpData.Gen.Lw; % Line weight for output graphics (admin)
Kf = InpData.Load.Kf;% Fatigue stress factor (adim)

%% Calculations
Sb = Kf*((M.*c)./I);          % Bending stress along beam (MPa)
Sbmax =  max(abs(Sb), [], 2); % Max bend. stress on beam for each load step(MPa)

%% Plot results
figure;
hold on;
for i = 1:size(Sb,1)
  for j = 1:size(Sb,3)
    plot (x(i,:), Sb(i,:,j), "--rd", "linewidth", Lw);
    xlabel ("x (mm)");
    ylabel ("SigmaB(x) (MPa)");
    title ("Bending Stress");
  endfor
endfor    
endfunction