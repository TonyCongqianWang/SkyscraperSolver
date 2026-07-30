#include "node_selection_score.h"
#include "math_utils.h"

/* Lookup table for selection counts 0..9.
   Initialized statically to the analytical values of (1 - x^p) / p for p = -2.0 */
double g_selection_lut[10] = {
	0.0,
	0.0,
	-0.375,
	-0.4444444444444444,
	-0.46875,
	-0.48,
	-0.4861111111111111,
	-0.4897959183673469,
	-0.4921875,
	-0.4938271604938271
};

void	init_selection_lut(double p)
{
	int		i;
	double	val;
	double	ln_x;

	g_selection_lut[0] = 0.0;
	i = 1;
	while (i <= 9)
	{
		if (p > 1e-4 || p < -1e-4)
		{
			val = (1.0 - custom_pow(i, p)) / p;
		}
		else
		{
			ln_x = custom_ln(i);
			/* Taylor series approximation for p close to 0 to avoid division by p */
			val = -ln_x - (p * ln_x * ln_x) / 2.0 - (p * p * ln_x * ln_x * ln_x) / 6.0;
		}
		g_selection_lut[i] = val;
		i++;
	}
}
