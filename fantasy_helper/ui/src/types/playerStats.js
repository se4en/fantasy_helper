/**
 * @typedef {Object} PlayersTableRow
 * @property {string} league_name
 * @property {string} name
 * @property {string} team_name
 * @property {string} [role]
 * @property {number} [price]
 * @property {number} [games]
 * @property {number} [minutes]
 * @property {number} [goals]
 * @property {number} [shots]
 * @property {number} [shots_on_target]
 * @property {number} [xg]
 * @property {number} [xg_np]
 * @property {number} [xg_xa]
 * @property {number} [xg_np_xa]
 * @property {number} [assists]
 * @property {number} [xa]
 * @property {number} [passes_into_penalty_area]
 * @property {number} [crosses_into_penalty_area]
 * @property {number} [touches_in_attacking_third]
 * @property {number} [touches_in_attacking_penalty_area]
 * @property {number} [carries_in_attacking_third]
 * @property {number} [carries_in_attacking_penalty_area]
 * @property {number} [sca]
 * @property {number} [gca]
 */

import { z } from 'zod'

export const PlayersTableRowSchema = z.object({
  league_name: z.string(),
  name: z.string(),
  team_name: z.string(),
  role: z.string().nullable().optional(),
  price: z.number().nullable().optional(),
  games: z.number().nullable().optional(),
  minutes: z.number().nullable().optional(),
  goals: z.number().nullable().optional(),
  shots: z.number().nullable().optional(),
  shots_on_target: z.number().nullable().optional(),
  xg: z.number().nullable().optional(),
  xg_np: z.number().nullable().optional(),
  xg_xa: z.number().nullable().optional(),
  xg_np_xa: z.number().nullable().optional(),
  assists: z.number().nullable().optional(),
  xa: z.number().nullable().optional(),
  passes_into_penalty_area: z.number().nullable().optional(),
  crosses_into_penalty_area: z.number().nullable().optional(),
  touches_in_attacking_third: z.number().nullable().optional(),
  touches_in_attacking_penalty_area: z.number().nullable().optional(),
  carries_in_attacking_third: z.number().nullable().optional(),
  carries_in_attacking_penalty_area: z.number().nullable().optional(),
  sca: z.number().nullable().optional(),
  gca: z.number().nullable().optional()
})

export default {
  PlayersTableRowSchema
}