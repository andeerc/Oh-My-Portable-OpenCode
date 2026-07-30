import { type PluginInput } from "@opencode-ai/plugin"
import { tool, type ToolDefinition } from "@opencode-ai/plugin/tool"
import { join, dirname } from "path"
import { readFile } from "fs/promises"
import { fileURLToPath } from "url"

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

interface ConductorCommandConfig {
  name: string
  description: string
  args: Record<string, any>
  requiresSetup?: boolean
  additionalContext?: (ctx: PluginInput, args: any) => Promise<Record<string, string>>
}

// Helper to load and process prompt templates
async function loadPrompt(
  filename: string,
  replacements: Record<string, string> = {},
) {
  // Try src/prompts first, then relative to project root
  const pathsToTry = [
    join(__dirname, "..", "..", "legacy", "conductor", "commands", "conductor", filename),
    join(__dirname, "..", "prompts", "conductor", filename.replace(".toml", ".json"))
  ]

  let content = ""
  let successPath = ""

  for (const p of pathsToTry) {
    try {
      content = await readFile(p, "utf-8")
      successPath = p
      break
    } catch (e) {
      continue
    }
  }

  if (!content) {
    console.error(`[Conductor] Error loading prompt ${filename}: Not found in any tried paths`)
    return {
      prompt: `SYSTEM ERROR: Failed to load prompt ${filename}`,
      description: "Error loading command",
    }
  }

  try {
    let promptText = ""
    let description = "Conductor Command"

    if (successPath.endsWith(".json")) {
      const parsed = JSON.parse(content)
      promptText = parsed.prompt || ""
      description = parsed.description || description
    } else {
      const descMatch = content.match(/description\s*=\s*"([^"]+)"/)
      description = descMatch ? descMatch[1] : description
      const promptMatch = content.match(/prompt\s*=\s*"""([\s\S]*?)"""/)
      promptText = promptMatch ? promptMatch[1] : ""
    }

    if (!promptText)
      throw new Error(`Could not parse prompt text from ${filename}`)

    const defaults = {
      templatesDir: join(dirname(__dirname), "templates"),
    }

    const finalReplacements = { ...defaults, ...replacements }
    for (const [key, value] of Object.entries(finalReplacements)) {
      promptText = promptText.replaceAll(`{{${key}}}`, value || "")
    }

    return { prompt: promptText, description: description }
  } catch (error) {
    console.error(`[Conductor] Error parsing prompt ${filename}:`, error)
    return {
      prompt: `SYSTEM ERROR: Failed to parse prompt ${filename}`,
      description: "Error parsing command",
    }
  }
}

export function createConductorCommand(config: ConductorCommandConfig) {
  return (ctx: PluginInput): ToolDefinition => {
    return tool({
      description: config.description,
      args: config.args,
      async execute(args: any, context: any) {
        // Get additional context if provided (this can override/extend args)
        const additionalContext = config.additionalContext
          ? await config.additionalContext(ctx, args)
          : {}

        // Merge additionalContext into replacements
        // additionalContext takes precedence and can provide custom mappings
        const replacements: Record<string, string> = { ...additionalContext }

        const { prompt } = await loadPrompt(config.name, replacements)
        return JSON.stringify({
          directives: prompt
        })
      },
    })
  }
}
