import { describe, it, expect, vi, beforeEach } from "vitest"
import { type PluginInput } from "@opencode-ai/plugin"
import {
  createSetupTool,
  createNewTrackTool,
  createImplementTool,
  createStatusTool,
  createRevertTool,
} from "./commands.js"
import { readFile } from "fs/promises"

// Mock fs/promises
vi.mock("fs/promises", () => ({
  readFile: vi.fn(),
}))

describe("Command Tools", () => {
  let mockCtx: PluginInput
  let mockToolContext: any
  
  beforeEach(() => {
    vi.clearAllMocks()

    mockCtx = {
      directory: "/test/project",
      isOMOActive: false,
    } as any

    mockToolContext = {
      sessionID: "test-session",
      messageID: "test-message",
    }

    // Default mocks - must use triple quotes for the regex in commandFactory
    vi.mocked(readFile).mockResolvedValue(`
description = "Test command"
prompt = """
Test prompt content
"""
`)
  })

  describe("createSetupTool", () => {
    it("should create a tool with correct description", () => {
      const tool = createSetupTool(mockCtx)
      expect(tool.description).toBe(
        "Directives lookup tool for scaffolding the project and setting up the Conductor environment",
      )
    })

    it("should return directives JSON string when executed", async () => {
      vi.mocked(readFile).mockResolvedValue(`
description = "Setup"
prompt = """Setup Prompt"""
`)
      const tool = createSetupTool(mockCtx)
      const result = await tool.execute({}, mockToolContext)
      expect(JSON.parse(result)).toEqual({ directives: "Setup Prompt" })
    })
  })

  describe("createNewTrackTool", () => {
    it("should create a tool with correct description", () => {
        const tool = createNewTrackTool(mockCtx)
        expect(tool.description).toBe(
          "Directives lookup tool for planning a track, generating track-specific spec documents and updating the tracks file",
        )
      })

    it("should have optional description argument", () => {
      const tool = createNewTrackTool(mockCtx)
      expect(tool.args).toHaveProperty("description")
    })

    it("should replace description in directives", async () => {
      vi.mocked(readFile).mockResolvedValue(`
description = "New Track"
prompt = """Track description: {{args}}"""
`)
      const tool = createNewTrackTool(mockCtx)
      const result = await tool.execute({ description: "Login feature" }, mockToolContext)
      expect(JSON.parse(result)).toEqual({ directives: "Track description: Login feature" })
    })
  })

  describe("createImplementTool", () => {
    it("should create a tool with correct description", () => {
        const tool = createImplementTool(mockCtx)
        expect(tool.description).toBe(
          "Directives lookup tool for executing the tasks defined in the specified track's plan",
        )
      })

    it("should have optional track_name argument", () => {
      const tool = createImplementTool(mockCtx)
      expect(tool.args).toHaveProperty("track_name")
    })

    it("should replace track_name in directives", async () => {
      vi.mocked(readFile).mockResolvedValue(`
description = "Implement"
prompt = """Track: {{track_name}}"""
`)
      const tool = createImplementTool(mockCtx)
      const result = await tool.execute({ track_name: "auth-track" }, mockToolContext)
      expect(JSON.parse(result)).toEqual({ directives: "Track: auth-track" })
    })

    it("should include strategy section in directives", async () => {
       vi.mocked(readFile).mockImplementation(async (path) => {
           if (typeof path === 'string' && path.endsWith("manual.md")) {
               return "Manual Strategy"
           }
           return `
description = "Implement"
prompt = """Strategy: {{strategy_section}}"""
`
       })

       const tool = createImplementTool(mockCtx)
       const result = await tool.execute({}, mockToolContext)
       expect(JSON.parse(result)).toEqual({ directives: "Strategy: Manual Strategy" })
    })
  })

  describe("createStatusTool", () => {
    it("should create a tool with correct description", () => {
        const tool = createStatusTool(mockCtx)
        expect(tool.description).toBe(
          "Directives lookup tool for displaying the current progress of the project",
        )
      })

    it("should execute and return directives", async () => {
      vi.mocked(readFile).mockResolvedValue(`
description = "Status"
prompt = """Status Prompt"""
`)
      const tool = createStatusTool(mockCtx)
      const result = await tool.execute({}, mockToolContext)
      expect(JSON.parse(result)).toEqual({ directives: "Status Prompt" })
    })
  })

  describe("createRevertTool", () => {
    it("should create a tool with correct description", () => {
        const tool = createRevertTool(mockCtx)
        expect(tool.description).toBe(
          "Directives lookup tool for reverting previous work",
        )
      })

    it("should replace target in directives", async () => {
      vi.mocked(readFile).mockResolvedValue(`
description = "Revert"
prompt = """Target: {{target}}"""
`)
      const tool = createRevertTool(mockCtx)
      const result = await tool.execute({ target: "track 1" }, mockToolContext)
      expect(JSON.parse(result)).toEqual({ directives: "Target: track 1" })
    })
  })

  describe("Error Handling", () => {
    it("should return error in directives if readFile fails", async () => {
      vi.mocked(readFile).mockRejectedValue(new Error("File not found"))
      const tool = createSetupTool(mockCtx)
      const result = await tool.execute({}, mockToolContext)
      expect(JSON.parse(result).directives).toContain("SYSTEM ERROR: Failed to load prompt")
    })
  })

  describe("Prompt Replacement", () => {
    it("should replace standard variables in directives", async () => {
      vi.mocked(readFile).mockResolvedValue(`
description = "Test"
prompt = """Templates: {{templatesDir}}"""
`)
      const tool = createNewTrackTool(mockCtx)
      const result = await tool.execute({}, mockToolContext)
      
      expect(JSON.parse(result).directives).toContain("Templates:")
    })
  })
})