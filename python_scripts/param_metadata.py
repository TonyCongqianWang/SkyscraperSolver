# PARAM_METADATA maps each SPSA parameter to (name, min_val, max_val, default_val, type)
PARAM_METADATA = [
    # ROUTING
    ("ROUTING_SHALLOW_RATIO", 0.0, 0.3, 0.222975482850643, float),
    ("ROUTING_MEDIUM_RATIO", 0.0, 0.5, 0.346611261752681, float),
    # ROOT
    ("ROOT_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.133056682040898, float),
    ("ROOT_CONSTR_MIN_UNSET", 0.0, 1.0, 0.0355884363571201, float),
    ("ROOT_CONSTR_MAX_UNSET", 0.0, 1.0, 0.94300944626904, float),
    ("ROOT_PERIOD_BASE", 1, 100, 3, int),
    ("ROOT_PERIOD_COEF1", 0, 10000, 941, int),
    ("ROOT_PERIOD_COEF2", 0, 150000, 11589, int),
    # SHALLOW
    ("SHALLOW_MIN_UNSET", 0.0, 0.5, 0.469777508074081, float),
    ("SHALLOW_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.171463907183973, float),
    ("SHALLOW_CONSTR_MIN_UNSET", 0.0, 1.0, 0.41366073436605, float),
    ("SHALLOW_CONSTR_MAX_UNSET", 0.0, 1.0, 0.847082378558519, float),
    ("SHALLOW_PERIOD_BASE", 1, 200, 14, int),
    ("SHALLOW_PERIOD_COEF1", 0, 15000, 159, int),
    ("SHALLOW_PERIOD_COEF2", 0, 150000, 6036, int),
    # MEDIUM
    ("MEDIUM_MIN_UNSET", 0.0, 0.5, 0.374687478840423, float),
    ("MEDIUM_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.155805632141164, float),
    ("MEDIUM_CONSTR_MIN_UNSET", 0.0, 1.0, 0.29774642733366, float),
    ("MEDIUM_CONSTR_MAX_UNSET", 0.0, 1.0, 0.74010638181629, float),
    ("MEDIUM_PERIOD_BASE", 1, 300, 57, int),
    ("MEDIUM_PERIOD_COEF1", 0, 10000, 6338, int),
    ("MEDIUM_PERIOD_COEF2", 0, 150000, 121706, int),
    # DEEP
    ("DEEP_MIN_UNSET", 0.0, 0.5, 0.14591158774683, float),
    ("DEEP_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.235087473816706, float),
    ("DEEP_CONSTR_MIN_UNSET", 0.0, 1.0, 0.496362077987333, float),
    ("DEEP_CONSTR_MAX_UNSET", 0.0, 1.0, 0.518850763514624, float),
    ("DEEP_PERIOD_BASE", 1, 400, 262, int),
    ("DEEP_PERIOD_COEF1", 0, 20000, 10826, int),
    ("DEEP_PERIOD_COEF2", 0, 150000, 87927, int),
    # NODE SELECT SELECTIVITY ROUTING
    ("SEL_REBUILD_PERIOD", 1, 10000, 1252, int),
    ("SEL_ORD2_COEFF", 0, 50000, 1709, int),
    ("SEL_ORD4_COEFF", 0, 500000, 66531, int),
    # ROOT LOOKAHEAD
    ("ROOT_LOOKAHEAD_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.151932027085723, float),
    ("ROOT_LOOKAHEAD_CONSTR_MIN_UNSET", 0.0, 1.0, 0.0291882141965284, float),
    ("ROOT_LOOKAHEAD_CONSTR_MAX_UNSET", 0.0, 1.0, 0.957192054459561, float),
    # SHALLOW LOOKAHEAD
    ("SHALLOW_LOOKAHEAD_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.14300904123259, float),
    ("SHALLOW_LOOKAHEAD_CONSTR_MIN_UNSET", 0.0, 1.0, 0.439043595345843, float),
    ("SHALLOW_LOOKAHEAD_CONSTR_MAX_UNSET", 0.0, 1.0, 0.77938473081213, float),
    # MEDIUM LOOKAHEAD
    ("MEDIUM_LOOKAHEAD_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.175898679226146, float),
    ("MEDIUM_LOOKAHEAD_CONSTR_MIN_UNSET", 0.0, 1.0, 0.333628153064668, float),
    ("MEDIUM_LOOKAHEAD_CONSTR_MAX_UNSET", 0.0, 1.0, 0.545293786455046, float),
    # DEEP LOOKAHEAD
    ("DEEP_LOOKAHEAD_GAC_UNSET_THRESHOLD", 0.1, 1.0, 0.218153206877934, float),
    ("DEEP_LOOKAHEAD_CONSTR_MIN_UNSET", 0.0, 1.0, 0.501391800430441, float),
    ("DEEP_LOOKAHEAD_CONSTR_MAX_UNSET", 0.0, 1.0, 0.544405049360684, float),
    # LOOKAHEAD DOWNGRADE FRACTIONS
    ("ROOT_LOOKAHEAD_DOWNGRADE_FRACTION", 0.0, 1.0, 0.0727673746639766, float),
    ("SHALLOW_LOOKAHEAD_DOWNGRADE_FRACTION", 0.0, 1.0, 0.00893946525610783, float),
    ("MEDIUM_LOOKAHEAD_DOWNGRADE_FRACTION", 0.0, 1.0, 0.0260732799012944, float),
    ("DEEP_LOOKAHEAD_DOWNGRADE_FRACTION", 0.0, 1.0, 0.0550035744246513, float),
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
