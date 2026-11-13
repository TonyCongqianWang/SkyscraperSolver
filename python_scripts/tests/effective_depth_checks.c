/* Focused C checks linked to production evaluation and routing code. */
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include "params_math.h"
#include "params_int.h"
#include "params_depth_arrays.h"
#include "entropy.h"
#include "pruning_configs.h"
#include "prune_strat_cfg_setup.h"
#include "strategy_routing.h"

const t_check_mode g_check_constr = {
	1, 0, 0, 0.0, {0.35, 0.70, 0}};
static t_prune_routine_cfg captured;

int run_pruning_routine(t_solver_state *p, const t_prune_routine_cfg *cfg, int tier)
{
	(void)p;
	(void)tier;
	captured = *cfg;
	return (-100);
}

int prune_strat_depth_bucket(t_solver_state *p, int b)
{
	(void)p;
	return (b);
}

static void near(double a, double b)
{
	assert(a - b < 1e-8 && b - a < 1e-8);
}

static void check_model(void)
{
	double *const warps[][3] = {
		{&g_depth_warp_0_le7, &g_depth_warp_1_le7, &g_depth_warp_2_le7},
		{&g_depth_warp_0_s8, &g_depth_warp_1_s8, &g_depth_warp_2_s8},
		{&g_depth_warp_0_s9, &g_depth_warp_1_s9, &g_depth_warp_2_s9},
		{&g_num_set_warp_0_le7, &g_num_set_warp_1_le7, &g_num_set_warp_2_le7},
		{&g_num_set_warp_0_s8, &g_num_set_warp_1_s8, &g_num_set_warp_2_s8},
		{&g_num_set_warp_0_s9, &g_num_set_warp_1_s9, &g_num_set_warp_2_s9}
	};
	int size, depth, set;
	double d, s, alpha;

	g_effective_depth_c0 = .5;
	g_effective_depth_cd = .1;
	g_effective_depth_cs = -.1;
	g_effective_depth_cdd = 0;
	g_effective_depth_cds = 0;
	g_effective_depth_css = 0;
	for (int group = 0; group < 6; group++)
		for (int knot = 0; knot < 3; knot++)
			*warps[group][knot] = .25 * (knot + 1);
	for (size = 4; size <= 9; size++)
	{
		for (depth = 0; depth <= size * size; depth++)
			for (set = 0; set <= size * size; set++)
			{
				d = (double)depth / (size * size);
				s = (double)set / (size * size);
				alpha = .5 + .1 * d - .1 * s;
				near(effective_depth(size, depth, size * size - set),
					(1 - alpha) * d + alpha * s);
			}
		for (set = 0; set < 3; set++)
		{
			near(get_depth_warp(size, set), .25 * (set + 1));
			near(get_num_set_warp(size, set), .25 * (set + 1));
		}
	}
	g_effective_depth_cdd = .7;
	g_effective_depth_cds = -.3;
	g_effective_depth_css = .2;
	d = .25;
	s = .75;
	alpha = .5 + .1*d - .1*s + .7*d*d - .3*d*s + .2*s*s;
	near(effective_depth(8, 16, 16), (1 - alpha)*d + alpha*s);
	g_effective_depth_cdd = 0;
	g_effective_depth_cds = 0;
	g_effective_depth_css = 0;
	g_num_set_warp_0_s8 = .8;
	g_num_set_warp_1_s8 = .2; /* Deliberately nonmonotone. */
	alpha = .5 + .1*.25 - .1*.8;
	near(effective_depth(8, 16, 48), (1-alpha)*.25 + alpha*.8);
	g_num_set_warp_0_s8 = .25;
	g_num_set_warp_1_s8 = .5;
}

static double interpolate(double t, const double *values)
{
	double w[SCHEDULE_KNOT_COUNT], result = 0;

	compute_catmull_weights(t, w);
	for (int i = 0; i < SCHEDULE_KNOT_COUNT; i++)
		result += w[i] * values[i];
	return (result);
}

static void check_spline_knots(void)
{
	const double knots[] = {0, 1.0/64, .25, .5, 1};
	const double values[] = {3, 9, -2, 4, 7};
	double w[SCHEDULE_KNOT_COUNT], left, right, eps = 1e-7;

	init_depth_arrays(8, 64);
	assert(g_depth_min_entropy[0] == g_min_entropy_p00);
	assert(g_depth_min_entropy[DEPTH_STRIDE + 1] == g_min_entropy_p1_64);
	for (int i = 0; i < SCHEDULE_KNOT_COUNT; i++)
	{
		compute_catmull_weights(knots[i], w);
		for (int j = 0; j < SCHEDULE_KNOT_COUNT; j++)
			near(w[j], i == j ? 1 : 0);
		near(interpolate(knots[i], values), values[i]);
		left = (values[i] - interpolate(knots[i] - eps, values)) / eps;
		right = (interpolate(knots[i] + eps, values) - values[i]) / eps;
		assert(left - right < .02 && right - left < .02);
	}
}

static void check_boundaries(void)
{
	double w[SCHEDULE_KNOT_COUNT], t;
	int i;

	for (i = -2; i <= 6; i++)
	{
		t = i * .25;
		compute_catmull_weights(t, w);
		near(w[0] + w[1] + w[2] + w[3] + w[4], 1);
		/* These knot values define an exactly linear schedule. */
		near(w[1]/64 + w[2]*.25 + w[3]*.5 + w[4], t);
	}
	g_effective_depth_cd = 0;
	g_effective_depth_cs = 0;
	g_effective_depth_c0 = 2;
	near(effective_depth(8, 16, 16), 1.25);
	g_effective_depth_c0 = -2;
	near(effective_depth(8, 16, 16), -.75);
	g_min_entropy_p00 = 0;
	g_min_entropy_p1_64 = 15625;
	g_min_entropy_p25 = 250000;
	g_min_entropy_p50 = 500000;
	g_min_entropy_p100 = 1000000;
	init_depth_arrays(8, 64);
	assert(g_depth_min_entropy[16 * DEPTH_STRIDE + 48] == 0);
	g_effective_depth_c0 = 2;
	init_depth_arrays(8, 64);
	assert(g_depth_min_entropy[16 * DEPTH_STRIDE + 48] == 1250000);
	assert(schedule_int(-10) == 0);
	assert(schedule_int(1e20) == INT_MAX);
	g_effective_depth_c0 = .5;
	g_effective_depth_cd = .1;
	g_effective_depth_cs = -.1;
}

static void check_node_schedules(void)
{
	t_solver_state p;
	t_node_state node;
	int a, b;
	double t;

	memset(&p, 0, sizeof(p));
	memset(&node, 0, sizeof(node));
	p.size = 8;
	p.squared_size = 64;
	p.cur_node = &node;
	node.tree.depth = 16;
	node.domain.num_unset = 48;
	init_depth_arrays(8, 64);
	a = prune_current_step(&p);
	node.domain.num_unset = 16;
	b = prune_current_step(&p);
	assert(a == 16 * DEPTH_STRIDE + 16);
	assert(b == 16 * DEPTH_STRIDE + 48);
	assert(g_depth_min_entropy[a] != g_depth_min_entropy[b]);
	t = effective_depth(8, 16, 16);
	assert(g_depth_min_entropy[b] == (int)(1000000*t + .5));
	assert(node.tree.depth == 16);
	node.tree.depth = 0;
	assert(prune_current_step(&p) == -100); /* Initial path unchanged. */
	p.prune_runs_count = 1;
	assert(prune_current_step(&p) == 48); /* Root uses the same table. */
	node.domain.num_unset = 64;
	assert(prune_current_step(&p) == 0);
	node.domain.num_unset = 62;
	assert(prune_current_step(&p) == 2);
	assert(g_depth_min_entropy[0] != g_depth_min_entropy[2]);
}

/* Independent domain scan, retained only as a test oracle. */
static int recompute_entropy(const t_node_state *node, int size)
{
	int total = 0;

	for (int i = 0; i < size * size; i++)
		total += get_log2_scaled(node->domain.num_cell_vals[i])
			* get_weight_cell(size) / ENTROPY_SCALE;
	for (int i = 0; i < 2 * size; i++)
		for (int v = 0; v < size; v++)
			total += get_log2_scaled(
				node->domain.constrs.num_val_positions[i][v])
				* get_weight_constr(size) / ENTROPY_SCALE;
	return (total);
}

/* Floating-point scaling can land just below an exact integer. */
static void check_scaled_cutoff(int actual, int expected)
{
	assert(actual == expected || actual == expected - 1);
}

static void check_scaling(void)
{
	t_prune_routine_cfg cfg;
	t_prune_limits lim;
	t_node_state empty;
	int size, i, v, e, base;
	double oldscale;

	memset(&lim, 0, sizeof(lim));
	g_global_entropy_multiplier_le7 = 1;
	g_global_entropy_multiplier_s8 = 1;
	g_global_entropy_multiplier_s9 = 1;
	base = 500000;
	lim.constr_global_min_entropy = base;
	lim.lh_constr_global_min_entropy = base;
	for (size = 4; size <= 9; size++)
	{
		memset(&empty, 0, sizeof(empty));
		for (i = 0; i < size*size; i++)
			empty.domain.num_cell_vals[i] = size;
		for (i = 0; i < 2*size; i++)
			for (v = 0; v < size; v++)
				empty.domain.constrs.num_val_positions[i][v] = size;
		e = compute_max_entropy(size);
		assert(e == recompute_entropy(&empty, size));
		check_scaled_cutoff(calc_effective_global_min_entropy(base, size), e / 2);
		setup_scheduled_prune_cfg(&cfg, &lim, size);
		check_scaled_cutoff(cfg.check_constr_global_min_entropy, e / 2);
		check_scaled_cutoff(cfg.lookahead.check_mode.constr.global_min_entropy, e / 2);
		init_prune_cfg(&cfg, 2, 0, size);
		assert(cfg.check_constr_global_min_entropy
			== calc_effective_global_min_entropy(
				g_initial_constr_global_min_entropy, size));
		assert(cfg.lookahead.check_mode.constr.global_min_entropy == 0);
		assert(calc_effective_global_min_entropy(1200000, size) > e);
	}
	g_global_entropy_multiplier_s8 = 2;
	e = compute_max_entropy(8);
	setup_scheduled_prune_cfg(&cfg, &lim, 8);
	check_scaled_cutoff(cfg.check_constr_global_min_entropy, e);
	check_scaled_cutoff(cfg.lookahead.check_mode.constr.global_min_entropy, e);
	init_prune_cfg(&cfg, 2, 0, 8);
	assert(cfg.check_constr_global_min_entropy
		== calc_effective_global_min_entropy(
			g_initial_constr_global_min_entropy, 8));
	/* Manual recentering leaves every effective threshold unchanged. */
	check_scaled_cutoff(calc_effective_global_min_entropy(base / 2, 8), e / 2);
	oldscale = g_weight_total_scale_s8;
	g_weight_total_scale_s8 *= 1.5;
	e = compute_max_entropy(8);
	check_scaled_cutoff(calc_effective_global_min_entropy(base, 8), e);
	g_weight_total_scale_s8 = oldscale;
	g_global_entropy_multiplier_s8 = 1;
}

static void check_grid_schedule_knots(void)
{
	const int positions[] = {0, 1, 16, 32, 64};
	const int constr[] = {
		g_constr_global_min_entropy_p00, g_constr_global_min_entropy_p1_64,
		g_constr_global_min_entropy_p25, g_constr_global_min_entropy_p50,
		g_constr_global_min_entropy_p100
	};
	const int lookahead[] = {
		g_lookahead_constr_global_min_entropy_p00,
		g_lookahead_constr_global_min_entropy_p1_64,
		g_lookahead_constr_global_min_entropy_p25,
		g_lookahead_constr_global_min_entropy_p50,
		g_lookahead_constr_global_min_entropy_p100
	};

	init_depth_arrays(8, 64);
	for (int knot = 0; knot < SCHEDULE_KNOT_COUNT; knot++)
	{
		int index = positions[knot] * (DEPTH_STRIDE + 1);

		assert(g_depth_constr_global_min_entropy[index] == constr[knot]);
		assert(g_depth_lookahead_constr_global_min_entropy[index]
			== lookahead[knot]);
	}
}

int main(void)
{
	check_model();
	check_spline_knots();
	check_boundaries();
	check_node_schedules();
	check_scaling();
	check_grid_schedule_knots();
	puts("effective-depth checks passed");
	return (0);
}
