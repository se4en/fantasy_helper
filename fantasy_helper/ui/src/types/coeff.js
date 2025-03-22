/**
 * @typedef {Object} CoeffTableRow
 * @property {string} team_name
 * @property {string} league_name
 * @property {string[]} [tour_names]
 * @property {number[]} [tour_numbers]
 * @property {string[]} [tour_rivals]
 * @property {string[]} [tour_match_types]
 * @property {number[]} [tour_attack_coeffs]
 * @property {number[]} [tour_deffence_coeffs]
 * @property {string[]} [tour_attack_colors]
 * @property {string[]} [tour_deffence_colors]
 */

import { z } from 'zod'

export const CoeffTableRowSchema = z.object({
  team_name: z.string(),
  league_name: z.string(),
  tour_names: z.array(z.string()).optional(),
  tour_numbers: z.array(z.number()).optional(),
  tour_rivals: z.array(z.string()).optional(),
  tour_match_types: z.array(z.string()).optional(),
  tour_attack_coeffs: z.array(z.number()).optional(),
  tour_deffence_coeffs: z.array(z.number()).optional(),
  tour_attack_colors: z.array(z.string()).optional(),
  tour_deffence_colors: z.array(z.string()).optional()
})

export default {
  CoeffTableRowSchema
}
