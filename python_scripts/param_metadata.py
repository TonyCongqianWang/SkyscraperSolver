# PARAM_METADATA maps each SPSA parameter to (name, min_val, max_val, default_val, type, perturb_scale)
PARAM_METADATA = [
    # ROUTING
    ("ROUTING_SHALLOW_RATIO_LE7", 0.0, 0.4, 0.0, float, 0.0204),
    ("ROUTING_SHALLOW_RATIO_S8", 0.0, 0.4, 0.0530791, float, 0.0156),
    ("ROUTING_SHALLOW_RATIO_S9", 0.0, 0.4, 0.2123164, float, 0.0123),
    ("ROUTING_MEDIUM_RATIO_LE7", 0.0, 0.6, 0.35049047, float, 0.0204),
    ("ROUTING_MEDIUM_RATIO_S8", 0.0, 0.6, 0.35049047, float, 0.0156),
    ("ROUTING_MEDIUM_RATIO_S9", 0.0, 0.6, 0.35049047, float, 0.0123),
    ("GLOBAL_ENTROPY_UNSET_BIAS_LE7", 100.0, 2000.0, 589.21814, float, 1.0),
    ("GLOBAL_ENTROPY_UNSET_BIAS_S8", 100.0, 2000.0, 469.79873, float, 1.0),
    ("GLOBAL_ENTROPY_UNSET_BIAS_S9", 100.0, 2000.0, 476.95816, float, 1.0),
    # ENTROPY WEIGHT REPARAMETERIZATION (Direction & Magnitude in Fixed-Point)
    ("WEIGHT_CELL_CONSTR_RATIO_FP_LE7", 1024, 12288, 8805, int, 1.0),
    ("WEIGHT_CELL_CONSTR_RATIO_FP_S8", 1024, 12288, 10490, int, 1.0),
    ("WEIGHT_CELL_CONSTR_RATIO_FP_S9", 1024, 12288, 5803, int, 1.0),
    ("WEIGHT_TOTAL_SCALE_FP_LE7", 256, 4096, 820, int, 1.0),
    ("WEIGHT_TOTAL_SCALE_FP_S8", 256, 4096, 626, int, 1.0),
    ("WEIGHT_TOTAL_SCALE_FP_S9", 256, 4096, 671, int, 1.0),
    # SELECTION HEURISTIC PARAMETERS (Ratio as Math, Power as Strategy)
    ("SEL_WEIGHT_CELL_CONSTR_RATIO_FP_LE7", 1024, 15360, 2634, int, 1.0),
    ("SEL_WEIGHT_CELL_CONSTR_RATIO_FP_S8", 1024, 15360, 2818, int, 1.0),
    ("SEL_WEIGHT_CELL_CONSTR_RATIO_FP_S9", 1024, 15360, 2297, int, 1.0),
    ("SEL_POWER_LE7", -2.0, 1.0, -0.826815, float, 0.1),
    ("SEL_POWER_S8", -2.0, 1.0, -0.80023576, float, 0.1),
    ("SEL_POWER_S9", -2.0, 1.0, -0.826815, float, 0.1),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_LE7", 0.0, 1.0, 0.15, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S8", 0.0, 1.0, 0.13188961, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S9", 0.0, 1.0, 0.15, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT1_LE7", 0.0, 1.0, 0.2, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S8", 0.0, 1.0, 0.20000811, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S9", 0.0, 1.0, 0.2, float, 0.05),
    ("LOOKAHEAD_ENTROPY_WEIGHT_LE7", 0.0, 50.0, 1.0, float, 0.5),
    ("LOOKAHEAD_ENTROPY_WEIGHT_S8", 0.0, 50.0, 1.0, float, 0.5),
    ("LOOKAHEAD_ENTROPY_WEIGHT_S9", 0.0, 50.0, 1.0, float, 0.5),
    # ROOT
    ("ROOT_MIN_ENTROPY", 0, 1027080, 79231, int, 1.0),
    ("ROOT_GAC_MIN_ENTROPY", 0, 1027080, 193438, int, 1.0),
    ("ROOT_CONSTR_MIN_ENTROPY", 0, 1027080, 69410, int, 1.0),
    ("ROOT_PERIOD_COEF_SCALE", 1.0, 1000.0, 50.150422, float, 1.0),
    ("ROOT_PERIOD_COEF_UNSET", 0.0, 100.0, 2.1159491, float, 1.0),
    # SHALLOW
    ("SHALLOW_MIN_ENTROPY", 0, 1027080, 229897, int, 1.0),
    ("SHALLOW_GAC_MIN_ENTROPY", 0, 1027080, 196078, int, 1.0),
    ("SHALLOW_CONSTR_MIN_ENTROPY", 0, 1027080, 389743, int, 1.0),
    ("SHALLOW_PERIOD_COEF_SCALE", 1.0, 1000.0, 98.648162, float, 1.0),
    ("SHALLOW_PERIOD_COEF_UNSET", 0.0, 100.0, 1.7226408, float, 1.0),
    # MEDIUM
    ("MEDIUM_MIN_ENTROPY", 0, 1027080, 226014, int, 1.0),
    ("MEDIUM_GAC_MIN_ENTROPY", 0, 1027080, 7434, int, 1.0),
    ("MEDIUM_CONSTR_MIN_ENTROPY", 0, 1027080, 143640, int, 1.0),
    ("MEDIUM_PERIOD_COEF_SCALE", 1.0, 2000.0, 233.25044, float, 1.0),
    ("MEDIUM_PERIOD_COEF_UNSET", 0.0, 100.0, 2.8826617, float, 1.0),
    # DEEP
    ("DEEP_MIN_ENTROPY", 0, 1027080, 265018, int, 1.0),
    ("DEEP_GAC_MIN_ENTROPY", 0, 1027080, 268150, int, 1.0),
    ("DEEP_CONSTR_MIN_ENTROPY", 0, 1027080, 481620, int, 1.0),
    ("DEEP_PERIOD_COEF_SCALE", 1.0, 5000.0, 628.32407, float, 1.0),
    ("DEEP_PERIOD_COEF_UNSET", 0.0, 100.0, 5.7752442, float, 1.0),
    # NODE SELECT SELECTIVITY ROUTING
    ("SEL_PERIOD_COEF_SQRT", 0.0, 100000.0, 481.90915, float, 1.0),
    ("SEL_PERIOD_COEF_INV", 0.0, 100000.0, 5021.7486, float, 1.0),
    # DYNAMIC ENTROPY LOOKAHEAD CONTINUATION THRESHOLDS & ESCALATION SLOPES
    ("ROOT_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 77570, int, 1.0),
    ("ROOT_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.4981356, float, 1.0),
    ("SHALLOW_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 191150, int, 1.0),
    ("SHALLOW_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.52974782, float, 1.0),
    ("MEDIUM_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 206216, int, 1.0),
    ("MEDIUM_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.46798817, float, 1.0),
    ("DEEP_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 236154, int, 1.0),
    ("DEEP_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.50943956, float, 1.0),
    # ROOT LOCAL/GLOBAL BOUNDS
    ("ROOT_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("ROOT_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.91827256, float, 0.2),
    ("ROOT_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 531954, int, 1.0),
    ("ROOT_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("ROOT_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.86924712, float, 0.2),
    ("ROOT_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 544461, int, 1.0),
    ("ROOT_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("ROOT_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.87477361, float, 0.2),
    ("ROOT_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 618517, int, 1.0),
    ("ROOT_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("ROOT_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.90492767, float, 0.2),
    ("ROOT_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 487994, int, 1.0),
    # SHALLOW LOCAL/GLOBAL BOUNDS
    ("SHALLOW_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("SHALLOW_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.89465724, float, 0.2),
    ("SHALLOW_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 653592, int, 1.0),
    ("SHALLOW_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("SHALLOW_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.84948695, float, 0.2),
    ("SHALLOW_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 391476, int, 1.0),
    ("SHALLOW_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("SHALLOW_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.82040691, float, 0.2),
    ("SHALLOW_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 786456, int, 1.0),
    ("SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.91029604, float, 0.2),
    ("SHALLOW_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 636327, int, 1.0),
    # MEDIUM LOCAL/GLOBAL BOUNDS
    ("MEDIUM_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("MEDIUM_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.92564241, float, 0.2),
    ("MEDIUM_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 550898, int, 1.0),
    ("MEDIUM_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("MEDIUM_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.85567988, float, 0.2),
    ("MEDIUM_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 238279, int, 1.0),
    ("MEDIUM_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("MEDIUM_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.77183745, float, 0.2),
    ("MEDIUM_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 528982, int, 1.0),
    ("MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.89658161, float, 0.2),
    ("MEDIUM_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 577466, int, 1.0),
    # DEEP LOCAL/GLOBAL BOUNDS
    ("DEEP_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("DEEP_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.84555875, float, 0.2),
    ("DEEP_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 516895, int, 1.0),
    ("DEEP_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("DEEP_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.86323531, float, 0.2),
    ("DEEP_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 455586, int, 1.0),
    ("DEEP_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("DEEP_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.95223394, float, 0.2),
    ("DEEP_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 408770, int, 1.0),
    ("DEEP_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0, float, 0.2),
    ("DEEP_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.82772885, float, 0.2),
    ("DEEP_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 504746, int, 1.0),
    # TIER MULTIPLIERS
    ("ROOT_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 2.1948125, float, 1.0),
    ("ROOT_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 3.6150508, float, 1.0),
    ("SHALLOW_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 2.0334088, float, 1.0),
    ("SHALLOW_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 4.2114755, float, 1.0),
    ("MEDIUM_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 2.3145012, float, 1.0),
    ("MEDIUM_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 4.7139034, float, 1.0),
    ("DEEP_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 1.9466372, float, 1.0),
    ("DEEP_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 3.3343315, float, 1.0),
    # Lookahead score blending weights & complement multiplier
    ("LOOKAHEAD_SCORE_AGE_LIMIT_RATIO", 0.0, 0.15, 0.06, float, 0.01),
    ("ROOT_PERIOD_TIER_COMPLEMENT_MULTIPLIER", 1.0, 20.0, 3.5972294, float, 0.5),
]

# PARAMETER_MAPPING maps each SPSA parameter to (C_filepath, C_variable_name, type)
PARAMETER_MAPPING = {
    "ROUTING_SHALLOW_RATIO_LE7": ("src/params_math.c", "g_routing_shallow_ratio_le7", "double"),
    "ROUTING_SHALLOW_RATIO_S8": ("src/params_math.c", "g_routing_shallow_ratio_s8", "double"),
    "ROUTING_SHALLOW_RATIO_S9": ("src/params_math.c", "g_routing_shallow_ratio_s9", "double"),
    "ROUTING_MEDIUM_RATIO_LE7": ("src/params_math.c", "g_routing_medium_ratio_le7", "double"),
    "ROUTING_MEDIUM_RATIO_S8": ("src/params_math.c", "g_routing_medium_ratio_s8", "double"),
    "ROUTING_MEDIUM_RATIO_S9": ("src/params_math.c", "g_routing_medium_ratio_s9", "double"),
    "GLOBAL_ENTROPY_UNSET_BIAS_LE7": ("src/params_math.c", "g_global_entropy_unset_bias_le7", "double"),
    "GLOBAL_ENTROPY_UNSET_BIAS_S8": ("src/params_math.c", "g_global_entropy_unset_bias_s8", "double"),
    "GLOBAL_ENTROPY_UNSET_BIAS_S9": ("src/params_math.c", "g_global_entropy_unset_bias_s9", "double"),
    # ENTROPY WEIGHT REPARAMETERIZATION (Direction & Magnitude in Fixed-Point)
    "WEIGHT_CELL_CONSTR_RATIO_FP_LE7": ("src/params_math.c", "g_weight_cell_constr_ratio_fp_le7", "int"),
    "WEIGHT_CELL_CONSTR_RATIO_FP_S8": ("src/params_math.c", "g_weight_cell_constr_ratio_fp_s8", "int"),
    "WEIGHT_CELL_CONSTR_RATIO_FP_S9": ("src/params_math.c", "g_weight_cell_constr_ratio_fp_s9", "int"),
    "SEL_WEIGHT_CELL_CONSTR_RATIO_FP_LE7": ("src/params_math.c", "g_sel_weight_cell_constr_ratio_fp_le7", "int"),
    "SEL_WEIGHT_CELL_CONSTR_RATIO_FP_S8": ("src/params_math.c", "g_sel_weight_cell_constr_ratio_fp_s8", "int"),
    "SEL_WEIGHT_CELL_CONSTR_RATIO_FP_S9": ("src/params_math.c", "g_sel_weight_cell_constr_ratio_fp_s9", "int"),
    "SEL_POWER_LE7": ("src/params_math.c", "g_sel_power_le7", "double"),
    "SEL_POWER_S8": ("src/params_math.c", "g_sel_power_s8", "double"),
    "SEL_POWER_S9": ("src/params_math.c", "g_sel_power_s9", "double"),
    "WEIGHT_TOTAL_SCALE_FP_LE7": ("src/params_math.c", "g_weight_total_scale_fp_le7", "int"),
    "WEIGHT_TOTAL_SCALE_FP_S8": ("src/params_math.c", "g_weight_total_scale_fp_s8", "int"),
    "WEIGHT_TOTAL_SCALE_FP_S9": ("src/params_math.c", "g_weight_total_scale_fp_s9", "int"),
    # ROOT
    "ROOT_MIN_ENTROPY": ("src/params_int.c", "g_root_min_entropy", "int"),
    "ROOT_GAC_MIN_ENTROPY": ("src/params_int.c", "g_root_gac_min_entropy", "int"),
    "ROOT_CONSTR_MIN_ENTROPY": ("src/params_int.c", "g_root_constr_min_entropy", "int"),
    "ROOT_PERIOD_COEF_SCALE": ("src/params_double.c", "g_root_period_coef_scale", "double"),
    "ROOT_PERIOD_COEF_UNSET": ("src/params_double.c", "g_root_period_coef_unset", "double"),
    # SHALLOW
    "SHALLOW_MIN_ENTROPY": ("src/params_int.c", "g_shallow_min_entropy", "int"),
    "SHALLOW_GAC_MIN_ENTROPY": ("src/params_int.c", "g_shallow_gac_min_entropy", "int"),
    "SHALLOW_CONSTR_MIN_ENTROPY": ("src/params_int.c", "g_shallow_constr_min_entropy", "int"),
    "SHALLOW_PERIOD_COEF_SCALE": ("src/params_double.c", "g_shallow_period_coef_scale", "double"),
    "SHALLOW_PERIOD_COEF_UNSET": ("src/params_double.c", "g_shallow_period_coef_unset", "double"),
    # MEDIUM
    "MEDIUM_MIN_ENTROPY": ("src/params_int.c", "g_medium_min_entropy", "int"),
    "MEDIUM_GAC_MIN_ENTROPY": ("src/params_int.c", "g_medium_gac_min_entropy", "int"),
    "MEDIUM_CONSTR_MIN_ENTROPY": ("src/params_int.c", "g_medium_constr_min_entropy", "int"),
    "MEDIUM_PERIOD_COEF_SCALE": ("src/params_double.c", "g_medium_period_coef_scale", "double"),
    "MEDIUM_PERIOD_COEF_UNSET": ("src/params_double.c", "g_medium_period_coef_unset", "double"),
    # DEEP
    "DEEP_MIN_ENTROPY": ("src/params_int.c", "g_deep_min_entropy", "int"),
    "DEEP_GAC_MIN_ENTROPY": ("src/params_int.c", "g_deep_gac_min_entropy", "int"),
    "DEEP_CONSTR_MIN_ENTROPY": ("src/params_int.c", "g_deep_constr_min_entropy", "int"),
    "DEEP_PERIOD_COEF_SCALE": ("src/params_double.c", "g_deep_period_coef_scale", "double"),
    "DEEP_PERIOD_COEF_UNSET": ("src/params_double.c", "g_deep_period_coef_unset", "double"),
    # SELECTIVITY
    "SEL_PERIOD_COEF_SQRT": ("src/params_double.c", "g_sel_period_coef_sqrt", "double"),
    "SEL_PERIOD_COEF_INV": ("src/params_double.c", "g_sel_period_coef_inv", "double"),
    # LOOKAHEAD CONTINUATION THRESHOLDS & ESCALATION SLOPES
    "ROOT_LOOKAHEAD_CONTINUE_MIN_ENTROPY": ("src/params_int.c", "g_root_lookahead_continue_min_entropy", "int"),
    "ROOT_LOOKAHEAD_CONTINUE_SLOPE": ("src/params_double.c", "g_root_lookahead_continue_slope", "double"),
    "SHALLOW_LOOKAHEAD_CONTINUE_MIN_ENTROPY": ("src/params_int.c", "g_shallow_lookahead_continue_min_entropy", "int"),
    "SHALLOW_LOOKAHEAD_CONTINUE_SLOPE": ("src/params_double.c", "g_shallow_lookahead_continue_slope", "double"),
    "MEDIUM_LOOKAHEAD_CONTINUE_MIN_ENTROPY": ("src/params_int.c", "g_medium_lookahead_continue_min_entropy", "int"),
    "MEDIUM_LOOKAHEAD_CONTINUE_SLOPE": ("src/params_double.c", "g_medium_lookahead_continue_slope", "double"),
    "DEEP_LOOKAHEAD_CONTINUE_MIN_ENTROPY": ("src/params_int.c", "g_deep_lookahead_continue_min_entropy", "int"),
    "DEEP_LOOKAHEAD_CONTINUE_SLOPE": ("src/params_double.c", "g_deep_lookahead_continue_slope", "double"),
    # ROOT LOCAL/GLOBAL BOUNDS
    "ROOT_GAC_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_root_gac_local_min_entropy", "double"),
    "ROOT_GAC_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_root_gac_local_max_entropy", "double"),
    "ROOT_GAC_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_root_gac_global_min_entropy", "int"),
    "ROOT_CONSTR_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_root_constr_local_min_entropy", "double"),
    "ROOT_CONSTR_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_root_constr_local_max_entropy", "double"),
    "ROOT_CONSTR_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_root_constr_global_min_entropy", "int"),
    "ROOT_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_root_lookahead_gac_local_min_entropy", "double"),
    "ROOT_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_root_lookahead_gac_local_max_entropy", "double"),
    "ROOT_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_root_lookahead_gac_global_min_entropy", "int"),
    "ROOT_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_root_lookahead_constr_local_min_entropy", "double"),
    "ROOT_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_root_lookahead_constr_local_max_entropy", "double"),
    "ROOT_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_root_lookahead_constr_global_min_entropy", "int"),
    # SHALLOW LOCAL/GLOBAL BOUNDS
    "SHALLOW_GAC_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_shallow_gac_local_min_entropy", "double"),
    "SHALLOW_GAC_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_shallow_gac_local_max_entropy", "double"),
    "SHALLOW_GAC_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_shallow_gac_global_min_entropy", "int"),
    "SHALLOW_CONSTR_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_shallow_constr_local_min_entropy", "double"),
    "SHALLOW_CONSTR_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_shallow_constr_local_max_entropy", "double"),
    "SHALLOW_CONSTR_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_shallow_constr_global_min_entropy", "int"),
    "SHALLOW_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_shallow_lookahead_gac_local_min_entropy", "double"),
    "SHALLOW_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_shallow_lookahead_gac_local_max_entropy", "double"),
    "SHALLOW_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_shallow_lookahead_gac_global_min_entropy", "int"),
    "SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_shallow_lookahead_constr_local_min_entropy", "double"),
    "SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_shallow_lookahead_constr_local_max_entropy", "double"),
    "SHALLOW_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_shallow_lookahead_constr_global_min_entropy", "int"),
    # MEDIUM LOCAL/GLOBAL BOUNDS
    "MEDIUM_GAC_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_medium_gac_local_min_entropy", "double"),
    "MEDIUM_GAC_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_medium_gac_local_max_entropy", "double"),
    "MEDIUM_GAC_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_medium_gac_global_min_entropy", "int"),
    "MEDIUM_CONSTR_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_medium_constr_local_min_entropy", "double"),
    "MEDIUM_CONSTR_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_medium_constr_local_max_entropy", "double"),
    "MEDIUM_CONSTR_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_medium_constr_global_min_entropy", "int"),
    "MEDIUM_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_medium_lookahead_gac_local_min_entropy", "double"),
    "MEDIUM_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_medium_lookahead_gac_local_max_entropy", "double"),
    "MEDIUM_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_medium_lookahead_gac_global_min_entropy", "int"),
    "MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_medium_lookahead_constr_local_min_entropy", "double"),
    "MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_medium_lookahead_constr_local_max_entropy", "double"),
    "MEDIUM_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_medium_lookahead_constr_global_min_entropy", "int"),
    # DEEP LOCAL/GLOBAL BOUNDS
    "DEEP_GAC_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_deep_gac_local_min_entropy", "double"),
    "DEEP_GAC_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_deep_gac_local_max_entropy", "double"),
    "DEEP_GAC_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_deep_gac_global_min_entropy", "int"),
    "DEEP_CONSTR_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_deep_constr_local_min_entropy", "double"),
    "DEEP_CONSTR_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_deep_constr_local_max_entropy", "double"),
    "DEEP_CONSTR_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_deep_constr_global_min_entropy", "int"),
    "DEEP_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_deep_lookahead_gac_local_min_entropy", "double"),
    "DEEP_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_deep_lookahead_gac_local_max_entropy", "double"),
    "DEEP_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_deep_lookahead_gac_global_min_entropy", "int"),
    "DEEP_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY": ("src/params_double.c", "g_deep_lookahead_constr_local_min_entropy", "double"),
    "DEEP_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY": ("src/params_double.c", "g_deep_lookahead_constr_local_max_entropy", "double"),
    "DEEP_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY": ("src/params_int.c", "g_deep_lookahead_constr_global_min_entropy", "int"),
    # TIER MULTIPLIERS
    "ROOT_PERIOD_TIER_MEDIUM_MULTIPLIER": ("src/params_double.c", "g_root_period_tier_medium_mult", "double"),
    "ROOT_PERIOD_TIER_HEAVY_MULTIPLIER": ("src/params_double.c", "g_root_period_tier_heavy_mult", "double"),
    "SHALLOW_PERIOD_TIER_MEDIUM_MULTIPLIER": ("src/params_double.c", "g_shallow_period_tier_medium_mult", "double"),
    "SHALLOW_PERIOD_TIER_HEAVY_MULTIPLIER": ("src/params_double.c", "g_shallow_period_tier_heavy_mult", "double"),
    "MEDIUM_PERIOD_TIER_MEDIUM_MULTIPLIER": ("src/params_double.c", "g_medium_period_tier_medium_mult", "double"),
    "MEDIUM_PERIOD_TIER_HEAVY_MULTIPLIER": ("src/params_double.c", "g_medium_period_tier_heavy_mult", "double"),
    "DEEP_PERIOD_TIER_MEDIUM_MULTIPLIER": ("src/params_double.c", "g_deep_period_tier_medium_mult", "double"),
    "DEEP_PERIOD_TIER_HEAVY_MULTIPLIER": ("src/params_double.c", "g_deep_period_tier_heavy_mult", "double"),
    "LOOKAHEAD_SCORE_WEIGHT_SPLIT0_LE7": ("src/params_math.c", "g_lookahead_score_weight_split0_le7", "double"),
    "LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S8": ("src/params_math.c", "g_lookahead_score_weight_split0_s8", "double"),
    "LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S9": ("src/params_math.c", "g_lookahead_score_weight_split0_s9", "double"),
    "LOOKAHEAD_SCORE_WEIGHT_SPLIT1_LE7": ("src/params_math.c", "g_lookahead_score_weight_split1_le7", "double"),
    "LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S8": ("src/params_math.c", "g_lookahead_score_weight_split1_s8", "double"),
    "LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S9": ("src/params_math.c", "g_lookahead_score_weight_split1_s9", "double"),
    "LOOKAHEAD_SCORE_AGE_LIMIT_RATIO": ("src/params_double.c", "g_lookahead_score_age_limit_ratio", "double"),
    "ROOT_PERIOD_TIER_COMPLEMENT_MULTIPLIER": ("src/params_double.c", "g_root_period_tier_complement_mult", "double"),
}

# PARAM_CONSTRAINTS defines linear constraints between parameters.
# Format: (param_min_name, param_max_name, eps)
# enforces: physical_value(param_min_name) <= physical_value(param_max_name) + eps
PARAM_CONSTRAINTS = [
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_LE7", "LOOKAHEAD_SCORE_WEIGHT_SPLIT1_LE7", 0.0),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S8", "LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S8", 0.0),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S9", "LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S9", 0.0),
    ("ROUTING_SHALLOW_RATIO_LE7", "ROUTING_MEDIUM_RATIO_LE7", 0.0),
    ("ROUTING_SHALLOW_RATIO_S8", "ROUTING_MEDIUM_RATIO_S8", 0.0),
    ("ROUTING_SHALLOW_RATIO_S9", "ROUTING_MEDIUM_RATIO_S9", 0.0),
    # ROOT
    ("ROOT_GAC_LOCAL_MIN_UNSET", "ROOT_GAC_LOCAL_MAX_UNSET", 0.05),
    ("ROOT_CONSTR_LOCAL_MIN_UNSET", "ROOT_CONSTR_LOCAL_MAX_UNSET", 0.05),
    ("ROOT_LOOKAHEAD_GAC_LOCAL_MIN_UNSET", "ROOT_LOOKAHEAD_GAC_LOCAL_MAX_UNSET", 0.05),
    ("ROOT_LOOKAHEAD_CONSTR_LOCAL_MIN_UNSET", "ROOT_LOOKAHEAD_CONSTR_LOCAL_MAX_UNSET", 0.05),
    # SHALLOW
    ("SHALLOW_GAC_LOCAL_MIN_UNSET", "SHALLOW_GAC_LOCAL_MAX_UNSET", 0.05),
    ("SHALLOW_CONSTR_LOCAL_MIN_UNSET", "SHALLOW_CONSTR_LOCAL_MAX_UNSET", 0.05),
    ("SHALLOW_LOOKAHEAD_GAC_LOCAL_MIN_UNSET", "SHALLOW_LOOKAHEAD_GAC_LOCAL_MAX_UNSET", 0.05),
    ("SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MIN_UNSET", "SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MAX_UNSET", 0.05),
    # MEDIUM
    ("MEDIUM_GAC_LOCAL_MIN_UNSET", "MEDIUM_GAC_LOCAL_MAX_UNSET", 0.05),
    ("MEDIUM_CONSTR_LOCAL_MIN_UNSET", "MEDIUM_CONSTR_LOCAL_MAX_UNSET", 0.05),
    ("MEDIUM_LOOKAHEAD_GAC_LOCAL_MIN_UNSET", "MEDIUM_LOOKAHEAD_GAC_LOCAL_MAX_UNSET", 0.05),
    ("MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MIN_UNSET", "MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MAX_UNSET", 0.05),
    # DEEP
    ("DEEP_GAC_LOCAL_MIN_UNSET", "DEEP_GAC_LOCAL_MAX_UNSET", 0.05),
    ("DEEP_CONSTR_LOCAL_MIN_UNSET", "DEEP_CONSTR_LOCAL_MAX_UNSET", 0.05),
    ("DEEP_LOOKAHEAD_GAC_LOCAL_MIN_UNSET", "DEEP_LOOKAHEAD_GAC_LOCAL_MAX_UNSET", 0.05),
    ("DEEP_LOOKAHEAD_CONSTR_LOCAL_MIN_UNSET", "DEEP_LOOKAHEAD_CONSTR_LOCAL_MAX_UNSET", 0.05),
]

# Dynamically classify parameters to prevent future maintainability issues
STRATEGY_PARAM_NAMES = set()
MATH_PARAM_GROUPS = {
    "all": set(),
    "7": set(),
    "8": set(),
    "9": set()
}

for name, *etc in PARAM_METADATA:
    if "_BIAS" in name or "_FP" in name or "SEL_POWER" in name or "SPLIT" in name or "ENTROPY_WEIGHT" in name or "ROUTING" in name:
        if name.endswith("_LE7"):
            MATH_PARAM_GROUPS["7"].add(name)
        elif name.endswith("_S8"):
            MATH_PARAM_GROUPS["8"].add(name)
        elif name.endswith("_S9"):
            MATH_PARAM_GROUPS["9"].add(name)
        else:
            MATH_PARAM_GROUPS["all"].add(name)
    else:
        STRATEGY_PARAM_NAMES.add(name)

def get_active_param_names(tune_mode, size):
    """
    Returns the set of parameter names that should be active for SPSA tuning
    based on the tune_mode ('all', 'math', 'strategy') and puzzle size.
    """
    active_math = set(MATH_PARAM_GROUPS["all"])
    if str(size) in MATH_PARAM_GROUPS:
        active_math.update(MATH_PARAM_GROUPS[str(size)])

    if tune_mode == "math":
        return active_math
    elif tune_mode == "strategy":
        return STRATEGY_PARAM_NAMES
    else:
        # tune_mode == "all"
        return STRATEGY_PARAM_NAMES.union(active_math)

