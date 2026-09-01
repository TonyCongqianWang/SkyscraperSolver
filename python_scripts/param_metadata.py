# PARAM_METADATA maps each SPSA parameter to (name, min_val, max_val, default_val, type, perturb_scale)
PARAM_METADATA = [
    # ROUTING
    ("ROUTING_SHALLOW_RATIO_LE7", 0.0, 0.4, 0, float, 0.0204),
    ("ROUTING_SHALLOW_RATIO_S8", 0.0, 0.4, 0.0390625, float, 0.0156),
    ("ROUTING_SHALLOW_RATIO_S9", 0.0, 0.4, 0.210648617674064, float, 0.0123),
    ("ROUTING_MEDIUM_RATIO_LE7", 0.0, 0.6, 0.35049047, float, 0.0204),
    ("ROUTING_MEDIUM_RATIO_S8", 0.0, 0.6, 0.322392069516352, float, 0.0156),
    ("ROUTING_MEDIUM_RATIO_S9", 0.0, 0.6, 0.353331059327943, float, 0.0123),
    ("GLOBAL_ENTROPY_UNSET_BIAS_LE7", 100.0, 2000.0, 589.21814, float, 1.0),
    ("GLOBAL_ENTROPY_UNSET_BIAS_S8", 100.0, 2000.0, 436.290916957699, float, 1.0),
    ("GLOBAL_ENTROPY_UNSET_BIAS_S9", 100.0, 2000.0, 469.673935244143, float, 1.0),
    # ENTROPY WEIGHTS
    ("WEIGHT_CELL_CONSTR_RATIO_LE7", 0.0, 1.0, 0.692852818894837, float, 0.7),
    ("WEIGHT_CELL_CONSTR_RATIO_S8", 0.0, 1.0, 0.758835955547021, float, 0.7),
    ("WEIGHT_CELL_CONSTR_RATIO_S9", 0.0, 1.0, 0.598164743553915, float, 0.7),
    ("WEIGHT_TOTAL_SCALE_LE7", 1000.0, 8000.0, 5182.36527747058, float, 0.5),
    ("WEIGHT_TOTAL_SCALE_S8", 1000.0, 8000.0, 2261.39985332911, float, 0.5),
    ("WEIGHT_TOTAL_SCALE_S9", 1000.0, 8000.0, 3799.98269739279, float, 0.5),
    # SELECTION HEURISTIC PARAMETERS
    ("SEL_WEIGHT_CELL_CONSTR_RATIO_LE7", 0.0, 1.0, 0.0545372275412134, float, 0.2),
    ("SEL_WEIGHT_CELL_CONSTR_RATIO_S8", 0.0, 1.0, 0.0143755386270659, float, 0.2),
    ("SEL_WEIGHT_CELL_CONSTR_RATIO_S9", 0.0, 1.0, 0.0513865534728712, float, 0.2),
    ("SEL_POWER_LE7", -2.0, 1.0, -0.826815000000003, float, 0.05),
    ("SEL_POWER_S8", -2.0, 1.0, -0.696103680477042, float, 0.05),
    ("SEL_POWER_S9", -2.0, 1.0, -0.818181088010847, float, 0.05),
    # LOOKAHEAD PARAMETERS
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_LE7", 0.0, 1.0, 0.15, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S8", 0.0, 1.0, 0.181565869043364, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S9", 0.0, 1.0, 0.178794927177966, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT1_LE7", 0.0, 1.0, 0.2, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S8", 0.0, 1.0, 0.192596066691939, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S9", 0.0, 1.0, 0.202829822178296, float, 0.05),
    ("LOOKAHEAD_ENTROPY_WEIGHT_LE7", 0.0, 0.5, 0.02, float, 1.0),
    ("LOOKAHEAD_ENTROPY_WEIGHT_S8", 0.0, 0.5, 0.022, float, 1.0),
    ("LOOKAHEAD_ENTROPY_WEIGHT_S9", 0.0, 0.5, 0.02, float, 1.0),
    ("LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_LE7", 0.0, 0.1, 0.0534747000000001, float, 0.02),
    ("LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_S8", 0.0, 0.1, 0.0534747287353331, float, 0.02),
    ("LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_S9", 0.0, 0.1, 0.0523209059335327, float, 0.02),
    # ROOT
    ("ROOT_MIN_ENTROPY", 0, 1027080, 50680, int, 0.1),
    ("ROOT_GAC_MIN_ENTROPY", 0, 1027080, 175722, int, 0.1),
    ("ROOT_CONSTR_MIN_ENTROPY", 0, 1027080, 70827, int, 0.1),
    ("ROOT_PERIOD_COEF_SCALE", 1.0, 1000.0, 111.731021685774, float, 0.3),
    ("ROOT_PERIOD_COEF_UNSET", 0.0, 30.0, 9.26481735770976, float, 0.3),
    # SHALLOW
    ("SHALLOW_MIN_ENTROPY", 0, 1027080, 149508, int, 0.1),
    ("SHALLOW_GAC_MIN_ENTROPY", 0, 1027080, 152151, int, 0.1),
    ("SHALLOW_CONSTR_MIN_ENTROPY", 0, 1027080, 319892, int, 0.1),
    ("SHALLOW_PERIOD_COEF_SCALE", 1.0, 1000.0, 87.3846102750979, float, 0.3),
    ("SHALLOW_PERIOD_COEF_UNSET", 0.0, 30.0, 4.32560371025585, float, 0.3),
    # MEDIUM
    ("MEDIUM_MIN_ENTROPY", 0, 1027080, 127923, int, 0.1),
    ("MEDIUM_GAC_MIN_ENTROPY", 0, 1027080, 33515, int, 0.1),
    ("MEDIUM_CONSTR_MIN_ENTROPY", 0, 1027080, 166224, int, 0.1),
    ("MEDIUM_PERIOD_COEF_SCALE", 1.0, 2000.0, 133.177544738375, float, 0.3),
    ("MEDIUM_PERIOD_COEF_UNSET", 0.0, 30.0, 2.90474630514197, float, 0.3),
    # DEEP
    ("DEEP_MIN_ENTROPY", 0, 1027080, 269561, int, 0.1),
    ("DEEP_GAC_MIN_ENTROPY", 0, 1027080, 220473, int, 0.1),
    ("DEEP_CONSTR_MIN_ENTROPY", 0, 1027080, 445200, int, 0.1),
    ("DEEP_PERIOD_COEF_SCALE", 1.0, 5000.0, 600.510059511723, float, 0.3),
    ("DEEP_PERIOD_COEF_UNSET", 0.0, 30.0, 6.35293883168798, float, 0.3),
    # NODE SELECT SELECTIVITY ROUTING
    ("SEL_PERIOD_COEF_SQRT", 0.0, 15000.0, 2862.76093848253, float, 0.3),
    ("SEL_PERIOD_COEF_INV", 0.0, 50000.0, 15487, float, 0.3),
    # DYNAMIC ENTROPY LOOKAHEAD CONTINUATION THRESHOLDS & ESCALATION SLOPES
    ("ROOT_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 66316, int, 0.1),
    ("ROOT_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.724384730313047, float, 1.0),
    ("SHALLOW_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 189818, int, 0.1),
    ("SHALLOW_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.735069156876668, float, 1.0),
    ("MEDIUM_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 194499, int, 0.1),
    ("MEDIUM_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.374840166143043, float, 1.0),
    ("DEEP_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 250126, int, 0.1),
    ("DEEP_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.664157080076718, float, 1.0),
    # ROOT LOCAL/GLOBAL BOUNDS
    ("ROOT_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0458390041145359, float, 0.2),
    ("ROOT_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.906415199248187, float, 0.2),
    ("ROOT_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 573985, int, 0.1),
    ("ROOT_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0105656312921839, float, 0.2),
    ("ROOT_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.871478422729019, float, 0.2),
    ("ROOT_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 512516, int, 0.1),
    ("ROOT_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0448673130813842, float, 0.2),
    ("ROOT_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.881171226526941, float, 0.2),
    ("ROOT_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 633838, int, 0.1),
    ("ROOT_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0305059331999758, float, 0.2),
    ("ROOT_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.914291343617541, float, 0.2),
    ("ROOT_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 436088, int, 0.1),
    # SHALLOW LOCAL/GLOBAL BOUNDS
    ("SHALLOW_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0804376357060443, float, 0.2),
    ("SHALLOW_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.854464847872937, float, 0.2),
    ("SHALLOW_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 570160, int, 0.1),
    ("SHALLOW_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0332725995128711, float, 0.2),
    ("SHALLOW_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.862409376695231, float, 0.2),
    ("SHALLOW_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 347490, int, 0.1),
    ("SHALLOW_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0463466061324348, float, 0.2),
    ("SHALLOW_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.79256166945128, float, 0.2),
    ("SHALLOW_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 823688, int, 0.1),
    ("SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0377146103397959, float, 0.2),
    ("SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.866584516467528, float, 0.2),
    ("SHALLOW_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 697158, int, 0.1),
    # MEDIUM LOCAL/GLOBAL BOUNDS
    ("MEDIUM_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0598569662866011, float, 0.2),
    ("MEDIUM_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.950177639862868, float, 0.2),
    ("MEDIUM_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 543568, int, 0.1),
    ("MEDIUM_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.11779781042747, float, 0.2),
    ("MEDIUM_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.872757627159424, float, 0.2),
    ("MEDIUM_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 275389, int, 0.1),
    ("MEDIUM_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0586106379727954, float, 0.2),
    ("MEDIUM_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.779977706835724, float, 0.2),
    ("MEDIUM_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 481707, int, 0.1),
    ("MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0319779083430731, float, 0.2),
    ("MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.935300209799804, float, 0.2),
    ("MEDIUM_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 546824, int, 0.1),
    # DEEP LOCAL/GLOBAL BOUNDS
    ("DEEP_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.00313086566797632, float, 0.2),
    ("DEEP_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.802848174098503, float, 0.2),
    ("DEEP_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 577785, int, 0.1),
    ("DEEP_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0280884163432876, float, 0.2),
    ("DEEP_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.832767577679931, float, 0.2),
    ("DEEP_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 434819, int, 0.1),
    ("DEEP_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.00590201925668926, float, 0.2),
    ("DEEP_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.935961996525297, float, 0.2),
    ("DEEP_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 415616, int, 0.1),
    ("DEEP_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0565751684522854, float, 0.2),
    ("DEEP_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.833128803512528, float, 0.2),
    ("DEEP_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 466615, int, 0.1),
    # TIER MULTIPLIERS
    ("ROOT_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 2.17483810796407, float, 0.4),
    ("ROOT_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 3.78927231786481, float, 0.4),
    ("ROOT_PERIOD_TIER_COMPLEMENT_MULTIPLIER", 1.0, 20.0, 4.27745526176766, float, 0.4),
    ("SHALLOW_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 1.97534613804766, float, 0.4),
    ("SHALLOW_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 3.99669378231049, float, 0.4),
    ("MEDIUM_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 2.84201822406732, float, 0.4),
    ("MEDIUM_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 5.01874410362026, float, 0.4),
    ("DEEP_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 1.94203139690121, float, 0.4),
    ("DEEP_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 4.01609990319944, float, 0.4),
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
    "WEIGHT_CELL_CONSTR_RATIO_LE7": ("src/params_math.c", "g_weight_cell_constr_ratio_le7", "double"),
    "WEIGHT_CELL_CONSTR_RATIO_S8": ("src/params_math.c", "g_weight_cell_constr_ratio_s8", "double"),
    "WEIGHT_CELL_CONSTR_RATIO_S9": ("src/params_math.c", "g_weight_cell_constr_ratio_s9", "double"),
    "SEL_WEIGHT_CELL_CONSTR_RATIO_LE7": ("src/params_math.c", "g_sel_weight_cell_constr_ratio_le7", "double"),
    "SEL_WEIGHT_CELL_CONSTR_RATIO_S8": ("src/params_math.c", "g_sel_weight_cell_constr_ratio_s8", "double"),
    "SEL_WEIGHT_CELL_CONSTR_RATIO_S9": ("src/params_math.c", "g_sel_weight_cell_constr_ratio_s9", "double"),
    "SEL_POWER_LE7": ("src/params_math.c", "g_sel_power_le7", "double"),
    "SEL_POWER_S8": ("src/params_math.c", "g_sel_power_s8", "double"),
    "SEL_POWER_S9": ("src/params_math.c", "g_sel_power_s9", "double"),
    "WEIGHT_TOTAL_SCALE_LE7": ("src/params_math.c", "g_weight_total_scale_le7", "double"),
    "WEIGHT_TOTAL_SCALE_S8": ("src/params_math.c", "g_weight_total_scale_s8", "double"),
    "WEIGHT_TOTAL_SCALE_S9": ("src/params_math.c", "g_weight_total_scale_s9", "double"),
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
    "LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_LE7": ("src/params_math.c", "g_lookahead_score_age_limit_ratio_le7", "double"),
    "LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_S8": ("src/params_math.c", "g_lookahead_score_age_limit_ratio_s8", "double"),
    "LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_S9": ("src/params_math.c", "g_lookahead_score_age_limit_ratio_s9", "double"),
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
    filepath, _, _ = PARAMETER_MAPPING.get(name, ("", "", ""))
    if filepath == "src/params_math.c":
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
