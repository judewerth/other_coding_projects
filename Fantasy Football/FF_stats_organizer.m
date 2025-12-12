function stats_rankings = FF_stats_organizer(year_range)

first_year = year_range(1);
current_year = year_range(2);

position = ["Overall" , "Quarterback" , "Running_Back" , "Wide_Receiver" , "Tight_End"];
position_prefix = ["NA" , "QB" , "RB" , "WR" , "TE"];

for y = first_year-1:current_year-1

    year = string(y);

    stats = load( strcat("Stats Data/stats_" , year , ".mat") ) ;
    % ADP = [Overall Rank , Round.Pick , Name , Position , ADP , STD , High
    % , Low , Times Drafted]
    stats_Raw = struct2cell(stats);
    stats_Raw = stats_Raw{1,1};

    old_team = ["KAN" , "OAK" , "LVR" , "SDG" , "SFO" , "TAM" , "NWE" , "GNB" , "NOR" , "STL"];
    new_team = ["KC"  , "LV"  , "LV"  , "LAC" , "SF"  , "TB"  , "NE"  , "GB"  , "NO"  , "LAR"];

    for i = 1:length(new_team)

        team_index = find(string(stats_Raw(:,2)) == old_team(i));

        for k = 1:length(team_index)

            kk = team_index(k);
            stats_Raw{kk,2} = new_team(i);

        end

    end

    for j = 1:length(position)

        if j == 1 

            position_rankings_year.(position(j)) = stats_Raw;

        else
        
            position_index = find( string(stats_Raw(:,3)) == position_prefix(j) );
            position_rankings_year.(position(j)) = stats_Raw(position_index , :);

        end
    
    end

    stats_rankings.(sprintf("x%d" , y)) = position_rankings_year;



end