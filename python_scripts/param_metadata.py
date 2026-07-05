# PARAM_METADATA maps each SPSA parameter to (name, min_val, max_val, default_val, type)
PARAM_METADATA = [
    # ROUTING
    ("ROUTING_SHALLOW_RATIO", 0.0, 0.3, 0.105231964035567, float),
    ("ROUTING_MEDIUM_RATIO", 0.0, 0.5, 0.352562620956447, float),
    # ROOT
    ("ROOT_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.165274680957807, float),
    ("ROOT_CONSTR_MIN_UNSET", 0.0, 1.0, 0.0336582283849937, float),
    ("ROOT_CONSTR_MAX_UNSET", 0.0, 1.0, 0.954904903727092, float),
    ("ROOT_PERIOD_BASE", 1, 100, 2, int),
    ("ROOT_PERIOD_COEF1", 0, 10000, 1208, int),
    ("ROOT_PERIOD_COEF2", 0, 150000, 13619, int),
    # SHALLOW
    ("SHALLOW_MIN_UNSET", 0.0, 0.5, 0.459793373311945, float),
    ("SHALLOW_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.129471248287378, float),
    ("SHALLOW_CONSTR_MIN_UNSET", 0.0, 1.0, 0.407682931942645, float),
    ("SHALLOW_CONSTR_MAX_UNSET", 0.0, 1.0, 0.817356591876012, float),
    ("SHALLOW_PERIOD_BASE", 1, 200, 14, int),
    ("SHALLOW_PERIOD_COEF1", 0, 15000, 1067, int),
    ("SHALLOW_PERIOD_COEF2", 0, 150000, 22580, int),
    # MEDIUM
    ("MEDIUM_MIN_UNSET", 0.0, 0.5, 0.344792003685814, float),
    ("MEDIUM_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.183326749800973, float),
    ("MEDIUM_CONSTR_MIN_UNSET", 0.0, 1.0, 0.300890167488498, float),
    ("MEDIUM_CONSTR_MAX_UNSET", 0.0, 1.0, 0.738752734627329, float),
    ("MEDIUM_PERIOD_BASE", 1, 300, 65, int),
    ("MEDIUM_PERIOD_COEF1", 0, 10000, 5877, int),
    ("MEDIUM_PERIOD_COEF2", 0, 150000, 87369, int),
    # DEEP
    ("DEEP_MIN_UNSET", 0.0, 0.5, 0.144440768499286, float),
    ("DEEP_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.241505401466146, float),
    ("DEEP_CONSTR_MIN_UNSET", 0.0, 1.0, 0.497582762441804, float),
    ("DEEP_CONSTR_MAX_UNSET", 0.0, 1.0, 0.536472818366295, float),
    ("DEEP_PERIOD_BASE", 1, 400, 237, int),
    ("DEEP_PERIOD_COEF1", 0, 20000, 11107, int),
    ("DEEP_PERIOD_COEF2", 0, 150000, 85321, int),
    # NODE SELECT SELECTIVITY ROUTING
    ("SEL_REBUILD_PERIOD", 1, 10000, 1053, int),
    ("SEL_ORD2_COEFF", 0, 50000, 1565, int),
    ("SEL_ORD4_COEFF", 0, 500000, 65430, int),
]

# PARAMETER_MAPPING maps each SPSA parameter to (C_filepath, C_variable_name, type)
PARAMETER_MAPPING = {
    # ROUTING
    "ROUTING_SHALLOW_RATIO": ("src/prune_strat_routing.c", "g_routing_shallow_ratio", "double"),
    "ROUTING_MEDIUM_RATIO": ("src/prune_strat_routing.c", "g_routing_medium_ratio", "double"),
    # ROOT
    "ROOT_GAC_UNSET_THRESHOLD": ("src/prune_strat_root.c", "g_gac_unset_threshold", "double"),
    "ROOT_CONSTR_MIN_UNSET": ("src/prune_strat_root.c", "g_constr_min_unset", "double"),
    "ROOT_CONSTR_MAX_UNSET": ("src/prune_strat_root.c", "g_constr_max_unset", "double"),
    "ROOT_PERIOD_BASE": ("src/prune_strat_root.c", "g_period_base", "int"),
    "ROOT_PERIOD_COEF1": ("src/prune_strat_root.c", "g_period_coef1", "int"),
    "ROOT_PERIOD_COEF2": ("src/prune_strat_root.c", "g_period_coef2", "int"),
    # SHALLOW
    "SHALLOW_MIN_UNSET": ("src/prune_strat_shallow.c", "g_min_unset_threshold", "double"),
    "SHALLOW_GAC_UNSET_THRESHOLD": ("src/prune_strat_shallow.c", "g_gac_unset_threshold", "double"),
    "SHALLOW_CONSTR_MIN_UNSET": ("src/prune_strat_shallow.c", "g_constr_min_unset", "double"),
    "SHALLOW_CONSTR_MAX_UNSET": ("src/prune_strat_shallow.c", "g_constr_max_unset", "double"),
    "SHALLOW_PERIOD_BASE": ("src/prune_strat_shallow.c", "g_period_base", "int"),
    "SHALLOW_PERIOD_COEF1": ("src/prune_strat_shallow.c", "g_period_coef1", "int"),
    "SHALLOW_PERIOD_COEF2": ("src/prune_strat_shallow.c", "g_period_coef2", "int"),
    # MEDIUM
    "MEDIUM_MIN_UNSET": ("src/prune_strat_medium.c", "g_min_unset_threshold", "double"),
    "MEDIUM_GAC_UNSET_THRESHOLD": ("src/prune_strat_medium.c", "g_gac_unset_threshold", "double"),
    "MEDIUM_CONSTR_MIN_UNSET": ("src/prune_strat_medium.c", "g_constr_min_unset", "double"),
    "MEDIUM_CONSTR_MAX_UNSET": ("src/prune_strat_medium.c", "g_constr_max_unset", "double"),
    "MEDIUM_PERIOD_BASE": ("src/prune_strat_medium.c", "g_period_base", "int"),
    "MEDIUM_PERIOD_COEF1": ("src/prune_strat_medium.c", "g_period_coef1", "int"),
    "MEDIUM_PERIOD_COEF2": ("src/prune_strat_medium.c", "g_period_coef2", "int"),
    # DEEP
    "DEEP_MIN_UNSET": ("src/prune_strat_deep.c", "g_min_unset_threshold", "double"),
    "DEEP_GAC_UNSET_THRESHOLD": ("src/prune_strat_deep.c", "g_gac_unset_threshold", "double"),
    "DEEP_CONSTR_MIN_UNSET": ("src/prune_strat_deep.c", "g_constr_min_unset", "double"),
    "DEEP_CONSTR_MAX_UNSET": ("src/prune_strat_deep.c", "g_constr_max_unset", "double"),
    "DEEP_PERIOD_BASE": ("src/prune_strat_deep.c", "g_period_base", "int"),
    "DEEP_PERIOD_COEF1": ("src/prune_strat_deep.c", "g_period_coef1", "int"),
    "DEEP_PERIOD_COEF2": ("src/prune_strat_deep.c", "g_period_coef2", "int"),
    # SELECTIVITY
    "SEL_REBUILD_PERIOD": ("src/sel_strat_routing.c", "g_sel_rebuild_period", "double"),
    "SEL_ORD2_COEFF": ("src/sel_strat_routing.c", "g_sel_ord2_coeff", "double"),
    "SEL_ORD4_COEFF": ("src/sel_strat_routing.c", "g_sel_ord4_coeff", "double"),
}
