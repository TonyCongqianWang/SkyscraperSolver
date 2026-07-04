# PARAM_METADATA maps each SPSA parameter to (name, min_val, max_val, default_val, type)
PARAM_METADATA = [
    # ROUTING
    ("ROUTING_SHALLOW_RATIO", 0.0, 0.3, 0.0646461686238843, float),
    ("ROUTING_MEDIUM_RATIO", 0.0, 0.5, 0.333318179241799, float),
    # ROOT
    ("ROOT_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.140490714394978, float),
    ("ROOT_CONSTR_MIN_UNSET", 0.0, 1.0, 0.0464864903980572, float),
    ("ROOT_CONSTR_MAX_UNSET", 0.0, 1.0, 0.924372902715597, float),
    ("ROOT_PERIOD_BASE", 1, 100, 5, int),
    ("ROOT_PERIOD_COEF1", 0, 10000, 676, int),
    ("ROOT_PERIOD_COEF2", 0, 150000, 12720, int),
    # SHALLOW
    ("SHALLOW_MIN_UNSET", 0.0, 0.5, 0.465142207191729, float),
    ("SHALLOW_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.129563777149174, float),
    ("SHALLOW_CONSTR_MIN_UNSET", 0.0, 1.0, 0.456587433207486, float),
    ("SHALLOW_CONSTR_MAX_UNSET", 0.0, 1.0, 0.805592863603281, float),
    ("SHALLOW_PERIOD_BASE", 1, 200, 12, int),
    ("SHALLOW_PERIOD_COEF1", 0, 15000, 2085, int),
    ("SHALLOW_PERIOD_COEF2", 0, 150000, 24557, int),
    # MEDIUM
    ("MEDIUM_MIN_UNSET", 0.0, 0.5, 0.331460558512209, float),
    ("MEDIUM_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.169360578209157, float),
    ("MEDIUM_CONSTR_MIN_UNSET", 0.0, 1.0, 0.384302782806575, float),
    ("MEDIUM_CONSTR_MAX_UNSET", 0.0, 1.0, 0.716575129002334, float),
    ("MEDIUM_PERIOD_BASE", 1, 300, 63, int),
    ("MEDIUM_PERIOD_COEF1", 0, 10000, 5749, int),
    ("MEDIUM_PERIOD_COEF2", 0, 150000, 93572, int),
    # DEEP
    ("DEEP_MIN_UNSET", 0.0, 0.5, 0.104902821314612, float),
    ("DEEP_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.222333167670072, float),
    ("DEEP_CONSTR_MIN_UNSET", 0.0, 1.0, 0.501920440623507, float),
    ("DEEP_CONSTR_MAX_UNSET", 0.0, 1.0, 0.514292446956472, float),
    ("DEEP_PERIOD_BASE", 1, 400, 235, int),
    ("DEEP_PERIOD_COEF1", 0, 20000, 12074, int),
    ("DEEP_PERIOD_COEF2", 0, 150000, 93932, int),
    # NODE SELECT SELECTIVITY ROUTING
    ("SEL_REBUILD_PERIOD", 1, 10000, 1439, int),
    ("SEL_ORD2_COEFF", 0, 50000, 1921.66666666667, int),
    ("SEL_ORD4_COEFF", 0, 500000, 77651.6666666667, int),
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
