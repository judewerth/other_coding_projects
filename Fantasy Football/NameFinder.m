function wrong_names = NameFinder(ADP , Stats , year_range)

fields_stats = fieldnames(Stats);
fields_adp = fieldnames(ADP);

for i = 1:diff(year_range)
    
    stat_data = Stats.(fields_stats{i+1});
    adp_data = ADP.(fields_adp{i});

    position_logical = contains(string( adp_data.Overall(:,4) ) , ["DEF" , "K"]);
    adp_data.Overall(position_logical,:) = [];

    adp_names = string(adp_data.Overall(:,3));

    names_logical = contains(adp_names , string(stat_data.Overall(:,1)));
    names_logical = ~names_logical;
    wrong_names{i} = adp_names(names_logical);

end

