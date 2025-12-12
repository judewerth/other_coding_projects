clear
clc

year_range = [2010 , 2023]; % [first year , current year]

ADP = FF_ADP_organizer(year_range);
% ADP = [ Overall Rank , Round.Pick , Name , Position , ADP , Standard Deviation ,
%         Highest Picked , Lowest Picked , Times Drafted , Positional Rank ]

Stats = FF_stats_organizer(year_range);

%%
% Stat Indexes
Ovr = 1:6; % Overall Stats - [ Name , Team , Position , Age , Games Played , Games Started ]
Pas = 7:11; % Passing Stats - [ Completions , Attempts , Yards , TDs , INTs ]
Rsh = 12:15; % Rushing Stats - [ Attempts , Yards , Yards/Attempt , TDs ]
Rcv = 16:20; % Recieving Stats - [ Targets , Receptions , Yards , Yards/Reception , TDs ]
Fmb = 21:22; % Fumbles - [ Total Fumbles , Fumbles Lost ]
Scr = 23:25; % Scoring - [ Total TDs , 2 Pts Made, 2 Pts Passed ]
Pts = 26:30; % Fantasy Points - [ Standard , PPR , Draft Kings , Fanduel , VBD(Pts-baseline) ]
Rnk = 31:32; % Rank - [ Position Rank , Overall Rank ]

%%

wrong_names = NameFinder(ADP , Stats , year_range);

%%
a = contains(string(Stats.x2015.Overall(:,1)) , "Breshad");
b = find(a);

%%
a = contains(string(ADP.x2015.Overall(:,3)) , "Steve Smith");
b = find(a);
