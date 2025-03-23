/**
 * @typedef {Object} CalendarTableRow
 * @property {string} team_name
 * @property {string} league_name
 * @property {string[]} [tour_names]
 * @property {number[]} [tour_numbers]
 * @property {string[]} [tour_rivals]
 * @property {string[]} [tour_match_types]
 * @property {string[]} [tour_points_colors]
 * @property {string[]} [tour_goals_colors]
 * @property {string[]} [tour_xg_colors]
 */

import { z } from 'zod'

export const CalendarTableRowSchema = z.object({
  team_name: z.string(),
  league_name: z.string(),
  tour_names: z.array(z.string()).optional(),
  tour_numbers: z.array(z.number()).optional(),
  tour_rivals: z.array(z.string()).optional(),
  tour_match_types: z.array(z.string()).optional(),
  tour_points_colors: z.array(z.string()).optional(),
  tour_goals_colors: z.array(z.string()).optional(),
  tour_xg_colors: z.array(z.string()).optional()
})

export default {
  CalendarTableRowSchema
}
