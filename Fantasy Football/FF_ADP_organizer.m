function ADP_rankings = FF_ADP_organizer(year_range)

first_year = year_range(1);
current_year = year_range(2);

position = ["Quarterback" , "Running_Back" , "Wide_Receiver" , ...
             "Tight_End" , "Defense" , "Kicker" , "Overall" ,];
position_prefix = ["QB" , "RB" , "WR" , "TE" , "DEF" , "PK" , "NA"];

for y = first_year:current_year

    year = string(y); % sometimes need strings

    adp = load( strcat("ADP Data/ADP_" , year , ".mat") ) ;
    % ADP = [Overall Rank , Round.Pick , Name , Position , ADP , STD , High
    % , Low , Times Drafted]
    ADP_Raw = struct2cell(adp); 
    ADP_Raw = ADP_Raw{1,1}; % go from 1x1 struct --> large cell
    
    % Name Changes
    if y == 1 % 2010

        ADP_Raw{76,3} = "Marion Barber III";
        ADP_Raw{81,3} = "Cadillac Williams";
        % Marion Hardesty is a year late on stats?
        ADP_Raw{134,3} = "Josh Cribbs";

    elseif y == 2 % 2011

        ADP_Raw{175,3} = "Marion Barber III";
        % No Peyton Manning

    elseif y == 4 % 2013

        ADP_Raw{73,3} = "Steve Smith Sr.";

    elseif y == 5 % 2014

        ADP_Raw{31,3} = "Le'Veon Bell";
        % No Ray Rice
        ADP_Raw{123,3} = "Steve Smith Sr.";

    elseif y == 6 % 2015

        ADP_Raw{3,3} = "Le'Veon Bell";
        ADP_Raw{11,3} = "C.J. Anderson";
        ADP_Raw{12,3} = "Odell Beckham Jr.";
        ADP_Raw{65,3} = "T.J. Yeldon";
        ADP_Raw{74,3} = "Steve Smith Sr.";
        % No Victor Cruz
        % No Perriman

    end

    if y == 2023

        ADP_Raw(:,6) = []; % removes bye week stats

    end

    for j = 1:length(position)

        if j == 7 % if it's an overall position

            position_rankings_year.(position(j)) = ADP_Raw; % record raw data

        else

            position_index = find( string(ADP_Raw(:,4)) == position_prefix(j) );

            for k = 1:length(position_index)

                ADP_Raw{position_index(k),11} = k;

            end


            position_rankings_year.(position(j)) = ADP_Raw(position_index , :);
            % record data with position = position prefix

        end
    
    end

    ADP_rankings.(sprintf("x%d" , y)) = position_rankings_year; 



end