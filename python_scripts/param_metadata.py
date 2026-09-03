# PARAM_METADATA maps each SPSA parameter to (name, min_val, max_val, default_val, type, perturb_scale)
PARAM_METADATA = [
    # ROUTING
    ("ROUTING_SHALLOW_RATIO_LE7", 0.0, 0.4, 0, float, 0.0204),
    ("ROUTING_SHALLOW_RATIO_S8", 0.0, 0.4, 0.00588665099307736, float, 0.0156),
    ("ROUTING_SHALLOW_RATIO_S9", 0.0, 0.4, 0.0761874860054367, float, 0.0123),
    ("ROUTING_MEDIUM_RATIO_LE7", 0.0, 0.6, 0.35049047, float, 0.0204),
    ("ROUTING_MEDIUM_RATIO_S8", 0.0, 0.6, 0.466336561502447, float, 0.0156),
    ("ROUTING_MEDIUM_RATIO_S9", 0.0, 0.6, 0.225161881929778, float, 0.0123),
    ("GLOBAL_ENTROPY_UNSET_BIAS_LE7", 100.0, 800.0, 589.21814, float, 1.0),
    ("GLOBAL_ENTROPY_UNSET_BIAS_S8", 100.0, 800.0, 506.662199222781, float, 1.0),
    ("GLOBAL_ENTROPY_UNSET_BIAS_S9", 100.0, 800.0, 587.333511480733, float, 1.0),
    # ENTROPY WEIGHTS
    ("WEIGHT_CELL_CONSTR_RATIO_LE7", 0.35, 0.85, 0.692852818894837, float, 0.7),
    ("WEIGHT_CELL_CONSTR_RATIO_S8", 0.35, 0.85, 0.649633500632426, float, 0.7),
    ("WEIGHT_CELL_CONSTR_RATIO_S9", 0.35, 0.85, 0.680760019876136, float, 0.7),
    ("WEIGHT_TOTAL_SCALE_LE7", 1000.0, 8000.0, 5182.36527747058, float, 0.5),
    ("WEIGHT_TOTAL_SCALE_S8", 1000.0, 8000.0, 2347.26562075443, float, 0.5),
    ("WEIGHT_TOTAL_SCALE_S9", 1000.0, 8000.0, 3916.90195482875, float, 0.5),
    # SELECTION HEURISTIC PARAMETERS
    ("SEL_WEIGHT_CELL_CONSTR_RATIO_LE7", 0.0, 1.0, 0.02, float, 0.2),
    ("SEL_WEIGHT_CELL_CONSTR_RATIO_S8", 0.0, 1.0, 0.0141203597304245, float, 0.2),
    ("SEL_WEIGHT_CELL_CONSTR_RATIO_S9", 0.0, 1.0, 0.0124053647819597, float, 0.2),
    ("SEL_POWER_LE7", -1.6, 0.5, -0.826815000000003, float, 0.02),
    ("SEL_POWER_S8", -1.6, 0.5, -0.66601614748835, float, 0.02),
    ("SEL_POWER_S9", -1.6, 0.5, -0.737959704581468, float, 0.02),
    # LOOKAHEAD PARAMETERS
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_LE7", 0.0, 1.0, 0.15, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S8", 0.0, 1.0, 0.0536762354747716, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT0_S9", 0.0, 1.0, 0.316722899871111, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT1_LE7", 0.0, 1.0, 0.6, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S8", 0.0, 1.0, 0.278736319808384, float, 0.05),
    ("LOOKAHEAD_SCORE_WEIGHT_SPLIT1_S9", 0.0, 1.0, 0.948468628078637, float, 0.05),
    ("LOOKAHEAD_ENTROPY_WEIGHT_LE7", 0.0, 0.5, 0.02, float, 1.0),
    ("LOOKAHEAD_ENTROPY_WEIGHT_S8", 0.0, 0.5, 0.0323049102434509, float, 1.0),
    ("LOOKAHEAD_ENTROPY_WEIGHT_S9", 0.0, 0.5, 0.02, float, 1.0),
    ("LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_LE7", 0.0, 0.1, 0.0534747000000001, float, 0.02),
    ("LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_S8", 0.0, 0.1, 0.0321528646927364, float, 0.02),
    ("LOOKAHEAD_SCORE_AGE_LIMIT_RATIO_S9", 0.0, 0.1, 0.0823221894503763, float, 0.02),
    # ROOT
    ("ROOT_MIN_ENTROPY", 0, 1027080, 66219, int, 0.1),
    ("ROOT_GAC_MIN_ENTROPY", 0, 1027080, 148122, int, 0.1),
    ("ROOT_CONSTR_MIN_ENTROPY", 0, 1027080, 22116, int, 0.1),
    ("ROOT_PERIOD_COEF_SCALE", 1.0, 1000.0, 43.9346057686299, float, 0.3),
    ("ROOT_PERIOD_COEF_UNSET", 0.0, 30.0, 6.2067092033546, float, 0.3),
    # SHALLOW
    ("SHALLOW_MIN_ENTROPY", 0, 1027080, 71369, int, 0.1),
    ("SHALLOW_GAC_MIN_ENTROPY", 0, 1027080, 93463, int, 0.1),
    ("SHALLOW_CONSTR_MIN_ENTROPY", 0, 1027080, 428397, int, 0.1),
    ("SHALLOW_PERIOD_COEF_SCALE", 1.0, 1000.0, 47.9093027086084, float, 0.3),
    ("SHALLOW_PERIOD_COEF_UNSET", 0.0, 30.0, 4.18182983465333, float, 0.3),
    # MEDIUM
    ("MEDIUM_MIN_ENTROPY", 0, 1027080, 85263, int, 0.1),
    ("MEDIUM_GAC_MIN_ENTROPY", 0, 1027080, 19634, int, 0.1),
    ("MEDIUM_CONSTR_MIN_ENTROPY", 0, 1027080, 251773, int, 0.1),
    ("MEDIUM_PERIOD_COEF_SCALE", 1.0, 2000.0, 15.6289709641174, float, 0.3),
    ("MEDIUM_PERIOD_COEF_UNSET", 0.0, 30.0, 4.95706586695345, float, 0.3),
    # DEEP
    ("DEEP_MIN_ENTROPY", 0, 1027080, 206780, int, 0.1),
    ("DEEP_GAC_MIN_ENTROPY", 0, 1027080, 284733, int, 0.1),
    ("DEEP_CONSTR_MIN_ENTROPY", 0, 1027080, 459551, int, 0.1),
    ("DEEP_PERIOD_COEF_SCALE", 1.0, 5000.0, 270.163183520381, float, 0.3),
    ("DEEP_PERIOD_COEF_UNSET", 0.0, 30.0, 6.38199855854598, float, 0.3),
    # NODE SELECT SELECTIVITY ROUTING
    ("SEL_PERIOD_COEF_SQRT", 0.0, 15000.0, 3423.60979599072, float, 0.3),
    ("SEL_PERIOD_COEF_INV", 0.0, 50000.0, 23244.0460412092, float, 0.3),
    # DYNAMIC ENTROPY LOOKAHEAD CONTINUATION THRESHOLDS & ESCALATION SLOPES
    ("ROOT_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 104797, int, 0.1),
    ("ROOT_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.350093226533919, float, 1.0),
    ("SHALLOW_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 115454, int, 0.1),
    ("SHALLOW_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.0429459216270553, float, 1.0),
    ("MEDIUM_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 160263, int, 0.1),
    ("MEDIUM_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.935627316564233, float, 1.0),
    ("DEEP_LOOKAHEAD_CONTINUE_MIN_ENTROPY", 0, 1027080, 316422, int, 0.1),
    ("DEEP_LOOKAHEAD_CONTINUE_SLOPE", 0.0, 5.0, 0.621550339120422, float, 1.0),
    # ROOT LOCAL/GLOBAL BOUNDS
    ("ROOT_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.026690672710213, float, 0.2),
    ("ROOT_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.987950800968543, float, 0.2),
    ("ROOT_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 530785, int, 0.1),
    ("ROOT_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.170813703890921, float, 0.2),
    ("ROOT_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.848036910685889, float, 0.2),
    ("ROOT_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 612080, int, 0.1),
    ("ROOT_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0751912837610927, float, 0.2),
    ("ROOT_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.831729076190113, float, 0.2),
    ("ROOT_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 615089, int, 0.1),
    ("ROOT_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0330051628834314, float, 0.2),
    ("ROOT_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.899825001665015, float, 0.2),
    ("ROOT_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 491281, int, 0.1),
    # SHALLOW LOCAL/GLOBAL BOUNDS
    ("SHALLOW_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0894172607114619, float, 0.2),
    ("SHALLOW_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.934698059533885, float, 0.2),
    ("SHALLOW_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 465278, int, 0.1),
    ("SHALLOW_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.037209341954151, float, 0.2),
    ("SHALLOW_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.86207032063023, float, 0.2),
    ("SHALLOW_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 380031, int, 0.1),
    ("SHALLOW_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0384142951307894, float, 0.2),
    ("SHALLOW_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.759457527292232, float, 0.2),
    ("SHALLOW_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 875256, int, 0.1),
    ("SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0222356041045843, float, 0.2),
    ("SHALLOW_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.757239835471637, float, 0.2),
    ("SHALLOW_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 674654, int, 0.1),
    # MEDIUM LOCAL/GLOBAL BOUNDS
    ("MEDIUM_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0649913190448645, float, 0.2),
    ("MEDIUM_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.958686590112447, float, 0.2),
    ("MEDIUM_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 654085, int, 0.1),
    ("MEDIUM_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.149312031789585, float, 0.2),
    ("MEDIUM_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.994628362285794, float, 0.2),
    ("MEDIUM_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 349927, int, 0.1),
    ("MEDIUM_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0623665473412272, float, 0.2),
    ("MEDIUM_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.82366703950379, float, 0.2),
    ("MEDIUM_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 587120, int, 0.1),
    ("MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.182094834387266, float, 0.2),
    ("MEDIUM_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.975935694953729, float, 0.2),
    ("MEDIUM_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 454055, int, 0.1),
    # DEEP LOCAL/GLOBAL BOUNDS
    ("DEEP_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.222081766105983, float, 0.2),
    ("DEEP_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.705285285336503, float, 0.2),
    ("DEEP_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 546240, int, 0.1),
    ("DEEP_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.106617509563436, float, 0.2),
    ("DEEP_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.910357600017636, float, 0.2),
    ("DEEP_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 360412, int, 0.1),
    ("DEEP_LOOKAHEAD_GAC_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0774560645307797, float, 0.2),
    ("DEEP_LOOKAHEAD_GAC_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.832536704247417, float, 0.2),
    ("DEEP_LOOKAHEAD_GAC_GLOBAL_MIN_ENTROPY", 0, 1027080, 503343, int, 0.1),
    ("DEEP_LOOKAHEAD_CONSTR_LOCAL_MIN_ENTROPY", 0.0, 1.0, 0.0171749554053868, float, 0.2),
    ("DEEP_LOOKAHEAD_CONSTR_LOCAL_MAX_ENTROPY", 0.0, 1.0, 0.772221212606661, float, 0.2),
    ("DEEP_LOOKAHEAD_CONSTR_GLOBAL_MIN_ENTROPY", 0, 1027080, 438120, int, 0.1),
    # TIER MULTIPLIERS
    ("ROOT_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 2.32900301655477, float, 0.4),
    ("ROOT_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 3.27975407200212, float, 0.4),
    ("ROOT_PERIOD_TIER_COMPLEMENT_MULTIPLIER", 1.0, 20.0, 7.29457954758155, float, 0.4),
    ("SHALLOW_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 1.99189511361632, float, 0.4),
    ("SHALLOW_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 2.0016955598909, float, 0.4),
    ("MEDIUM_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 2.24357411528509, float, 0.4),
    ("MEDIUM_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 5.15235872841329, float, 0.4),
    ("DEEP_PERIOD_TIER_MEDIUM_MULTIPLIER", 1.0, 10.0, 3.23487176330083, float, 0.4),
    ("DEEP_PERIOD_TIER_HEAVY_MULTIPLIER", 1.0, 20.0, 4.26423815300899, float, 0.4),
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
    "LOOKAHEAD_ENTROPY_WEIGHT_LE7": ("src/params_math.c", "g_lookahead_entropy_weight_le7", "double"),
    "LOOKAHEAD_ENTROPY_WEIGHT_S8": ("src/params_math.c", "g_lookahead_entropy_weight_s8", "double"),
    "LOOKAHEAD_ENTROPY_WEIGHT_S9": ("src/params_math.c", "g_lookahead_entropy_weight_s9", "double"),
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
