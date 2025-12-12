% Overall_Stats = Stats(1:6);
% Point_Stats = Stats(26:30);
% Rank_Stats = Stats(31:32);

fields_stats = fieldnames(Stats);
fields_adp = fieldnames(ADP);

for i = 3:length(fields_stats)

    stat_data = Stats.(fields_stats{i});
    adp_data = ADP.(fields_adp{i-1});
    
    fields_positions = fieldnames(stat_data);

    for j = 2:length(fields_positions)
        
        position_stat = stat_data.(fields_positions{j});
        position_adp = adp_data.(fields_positions{j});

        [players , y] = size(position_adp);
        position_results = zeros(players , 1);

        for k = 1:players

            player_name_index = strcmp(position_adp(k,3) , position_stat(:,1));

        end
        
        

    end


end

% final product --> ADP difference , PPG vs ADP , Pts vs ADP (only within
% positions)