/**
 * @typedef {Object} SportsPlayerDiff
 * @property {string} name
 * @property {string} league_name
 * @property {string} [team_name]
 * @property {string} [role]
 * @property {number} [price]
 * @property {number} [percent_ownership]
 * @property {number} [percent_ownership_diff]
 */

import { z } from 'zod'

export const SportsPlayerDiffSchema = z.object({
  name: z.string(),
  league_name: z.string(),
  team_name: z.string().nullable().optional(),
  role: z.string().nullable().optional(),
  price: z.number().nullable().optional(),
  percent_ownership: z.number().nullable().optional(),
  percent_ownership_diff: z.number().nullable().optional()
})

export default {
  SportsPlayerDiffSchema
}