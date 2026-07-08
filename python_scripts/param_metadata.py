# PARAM_METADATA maps each SPSA parameter to (name, min_val, max_val, default_val, type)
PARAM_METADATA = [
    # ROUTING
    ("ROUTING_SHALLOW_RATIO", 0.0, 0.3, 0.215855787126784, float),
    ("ROUTING_MEDIUM_RATIO", 0.0, 0.5, 0.346520612541537, float),
    # ROOT
    ("ROOT_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.143920157443799, float),
    ("ROOT_CONSTR_MIN_UNSET", 0.0, 1.0, 0.035873563315611, float),
    ("ROOT_CONSTR_MAX_UNSET", 0.0, 1.0, 0.923891739928943, float),
    ("ROOT_PERIOD_BASE", 1, 100, 2, int),
    ("ROOT_PERIOD_COEF1", 0, 10000, 1208, int),
    ("ROOT_PERIOD_COEF2", 0, 150000, 16254, int),
    # SHALLOW
    ("SHALLOW_MIN_UNSET", 0.0, 0.5, 0.466481843447906, float),
    ("SHALLOW_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.152515062371431, float),
    ("SHALLOW_CONSTR_MIN_UNSET", 0.0, 1.0, 0.425777239297, float),
    ("SHALLOW_CONSTR_MAX_UNSET", 0.0, 1.0, 0.845111519525614, float),
    ("SHALLOW_PERIOD_BASE", 1, 200, 14, int),
    ("SHALLOW_PERIOD_COEF1", 0, 15000, 36, int),
    ("SHALLOW_PERIOD_COEF2", 0, 150000, 3749, int),
    # MEDIUM
    ("MEDIUM_MIN_UNSET", 0.0, 0.5, 0.361145726672716, float),
    ("MEDIUM_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.151621196461338, float),
    ("MEDIUM_CONSTR_MIN_UNSET", 0.0, 1.0, 0.299117826398078, float),
    ("MEDIUM_CONSTR_MAX_UNSET", 0.0, 1.0, 0.722050556789232, float),
    ("MEDIUM_PERIOD_BASE", 1, 300, 55, int),
    ("MEDIUM_PERIOD_COEF1", 0, 10000, 5777, int),
    ("MEDIUM_PERIOD_COEF2", 0, 150000, 102451, int),
    # DEEP
    ("DEEP_MIN_UNSET", 0.0, 0.5, 0.14295167787013, float),
    ("DEEP_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.237059958525931, float),
    ("DEEP_CONSTR_MIN_UNSET", 0.0, 1.0, 0.488651109126663, float),
    ("DEEP_CONSTR_MAX_UNSET", 0.0, 1.0, 0.519217184307659, float),
    ("DEEP_PERIOD_BASE", 1, 400, 261, int),
    ("DEEP_PERIOD_COEF1", 0, 20000, 10704, int),
    ("DEEP_PERIOD_COEF2", 0, 150000, 87730, int),
    # NODE SELECT SELECTIVITY ROUTING
    ("SEL_REBUILD_PERIOD", 1, 10000, 1319, int),
    ("SEL_ORD2_COEFF", 0, 50000, 1934, int),
    ("SEL_ORD4_COEFF", 0, 500000, 70567, int),
    # ROOT LOOKAHEAD
    ("ROOT_LOOKAHEAD_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.156582006684324, float),
    ("ROOT_LOOKAHEAD_CONSTR_MIN_UNSET", 0.0, 1.0, 0.024354749662233, float),
    ("ROOT_LOOKAHEAD_CONSTR_MAX_UNSET", 0.0, 1.0, 0.94982042984025, float),
    # SHALLOW LOOKAHEAD
    ("SHALLOW_LOOKAHEAD_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.13121146904074, float),
    ("SHALLOW_LOOKAHEAD_CONSTR_MIN_UNSET", 0.0, 1.0, 0.43006196879305, float),
    ("SHALLOW_LOOKAHEAD_CONSTR_MAX_UNSET", 0.0, 1.0, 0.786714075389936, float),
    # MEDIUM LOOKAHEAD
    ("MEDIUM_LOOKAHEAD_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.181638091722184, float),
    ("MEDIUM_LOOKAHEAD_CONSTR_MIN_UNSET", 0.0, 1.0, 0.327923762846436, float),
    ("MEDIUM_LOOKAHEAD_CONSTR_MAX_UNSET", 0.0, 1.0, 0.577550735573339, float),
    # DEEP LOOKAHEAD
    ("DEEP_LOOKAHEAD_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.22197098278197, float),
    ("DEEP_LOOKAHEAD_CONSTR_MIN_UNSET", 0.0, 1.0, 0.491471635165191, float),
    ("DEEP_LOOKAHEAD_CONSTR_MAX_UNSET", 0.0, 1.0, 0.557961197383707, float),
    # LOOKAHEAD DOWNGRADE FRACTIONS
    ("ROOT_LOOKAHEAD_DOWNGRADE_FRACTION", 0.0, 1.0, 0.0899471128437557, float),
    ("SHALLOW_LOOKAHEAD_DOWNGRADE_FRACTION", 0.0, 1.0, 0.00780047208301022, float),
    ("MEDIUM_LOOKAHEAD_DOWNGRADE_FRACTION", 0.0, 1.0, 0.0140173146554256, float),
    ("DEEP_LOOKAHEAD_DOWNGRADE_FRACTION", 0.0, 1.0, 0.0637218563432554, float),
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
    # ROOT LOOKAHEAD
    "ROOT_LOOKAHEAD_GAC_UNSET_THRESHOLD": ("src/prune_strat_root.c", "g_lookahead_gac_unset_threshold", "double"),
    "ROOT_LOOKAHEAD_CONSTR_MIN_UNSET": ("src/prune_strat_root.c", "g_lookahead_constr_min_unset", "double"),
    "ROOT_LOOKAHEAD_CONSTR_MAX_UNSET": ("src/prune_strat_root.c", "g_lookahead_constr_max_unset", "double"),
    # SHALLOW LOOKAHEAD
    "SHALLOW_LOOKAHEAD_GAC_UNSET_THRESHOLD": ("src/prune_strat_shallow.c", "g_lookahead_gac_unset_threshold", "double"),
    "SHALLOW_LOOKAHEAD_CONSTR_MIN_UNSET": ("src/prune_strat_shallow.c", "g_lookahead_constr_min_unset", "double"),
    "SHALLOW_LOOKAHEAD_CONSTR_MAX_UNSET": ("src/prune_strat_shallow.c", "g_lookahead_constr_max_unset", "double"),
    # MEDIUM LOOKAHEAD
    "MEDIUM_LOOKAHEAD_GAC_UNSET_THRESHOLD": ("src/prune_strat_medium.c", "g_lookahead_gac_unset_threshold", "double"),
    "MEDIUM_LOOKAHEAD_CONSTR_MIN_UNSET": ("src/prune_strat_medium.c", "g_lookahead_constr_min_unset", "double"),
    "MEDIUM_LOOKAHEAD_CONSTR_MAX_UNSET": ("src/prune_strat_medium.c", "g_lookahead_constr_max_unset", "double"),
    # DEEP LOOKAHEAD
    "DEEP_LOOKAHEAD_GAC_UNSET_THRESHOLD": ("src/prune_strat_deep.c", "g_lookahead_gac_unset_threshold", "double"),
    "DEEP_LOOKAHEAD_CONSTR_MIN_UNSET": ("src/prune_strat_deep.c", "g_lookahead_constr_min_unset", "double"),
    "DEEP_LOOKAHEAD_CONSTR_MAX_UNSET": ("src/prune_strat_deep.c", "g_lookahead_constr_max_unset", "double"),
    # LOOKAHEAD DOWNGRADE FRACTIONS
    "ROOT_LOOKAHEAD_DOWNGRADE_FRACTION": ("src/prune_strat_root.c", "g_lookahead_downgrade_fraction", "double"),
    "SHALLOW_LOOKAHEAD_DOWNGRADE_FRACTION": ("src/prune_strat_shallow.c", "g_lookahead_downgrade_fraction", "double"),
    "MEDIUM_LOOKAHEAD_DOWNGRADE_FRACTION": ("src/prune_strat_medium.c", "g_lookahead_downgrade_fraction", "double"),
    "DEEP_LOOKAHEAD_DOWNGRADE_FRACTION": ("src/prune_strat_deep.c", "g_lookahead_downgrade_fraction", "double"),
}

# PARAM_CONSTRAINTS defines linear constraints between parameters.
# Format: (param_min_name, param_max_name, eps)
# enforces: physical_value(param_min_name) <= physical_value(param_max_name) + eps
PARAM_CONSTRAINTS = [
    # Main Propagation Constraints
    ("ROOT_CONSTR_MIN_UNSET", "ROOT_CONSTR_MAX_UNSET", 0.05),
    ("SHALLOW_CONSTR_MIN_UNSET", "SHALLOW_CONSTR_MAX_UNSET", 0.05),
    ("MEDIUM_CONSTR_MIN_UNSET", "MEDIUM_CONSTR_MAX_UNSET", 0.05),
    ("DEEP_CONSTR_MIN_UNSET", "DEEP_CONSTR_MAX_UNSET", 0.05),

    # Lookahead Propagation Constraints
    ("ROOT_LOOKAHEAD_CONSTR_MIN_UNSET", "ROOT_LOOKAHEAD_CONSTR_MAX_UNSET", 0.05),
    ("SHALLOW_LOOKAHEAD_CONSTR_MIN_UNSET", "SHALLOW_LOOKAHEAD_CONSTR_MAX_UNSET", 0.05),
    ("MEDIUM_LOOKAHEAD_CONSTR_MIN_UNSET", "MEDIUM_LOOKAHEAD_CONSTR_MAX_UNSET", 0.05),
    ("DEEP_LOOKAHEAD_CONSTR_MIN_UNSET", "DEEP_LOOKAHEAD_CONSTR_MAX_UNSET", 0.05),
]
