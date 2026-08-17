# Rapid Prototyping

This skill enables agents to establish task-specific iteration harnesses when asked to build or prototype a system.

Instead of writing all the files manually right away or getting stuck in open-ended generative loops where the human has to constantly point out errors, this skill sets up a bounded iterative environment.

## Philosophy

Rapid prototyping is best done by scaffolding a **Universal Harness** that encapsulates generation, evaluation, iteration, and escalation. 
1. **Separate Generator from Evaluator**: The generator builds the artifact. The evaluator strictly tests and grades the output based on immutable requirements.
2. **Immutable Specs**: Requirements are fixed and passed into the harness. To change the target behavior, you update the specification, not the output.
3. **Bounded Retries**: The harness iterates a maximum number of times before handing control back to the operator.
4. **Escalation Path**: If the system cannot converge or resolve ambiguous requirements, it fails safely, showing the user the exact discrepancy.
5. **Incorporate Feedback into the Process**: Fix the instructions to the generator or the evaluation logic rather than fixing the faulty artifacts directly.

## Workflow

When asked to prototype a system or construct a new task harness:

### Phase 1: Clarify the Goal (The "Grill Me" Approach)

Inspired by rapid iteration techniques, act as an interrogator to shape the human's fuzzy idea into a clear requirement specification. 
1. Ask exactly ONE clear, concise question at a time to narrow down the goal.
2. Clarify what constitutes "success" (e.g. "What should the evaluator measure?").
3. Determine the input data format and output requirements.
4. Keep asking until you can produce an explicit, immutable specification (the `spec.md`).

### Phase 2: Scaffold the Harness

Once the `spec.md` is complete, generate the harness skeleton in the user's workspace.
The harness must contain:
1. `generator`: A prompt script or agent execution template that takes the `spec.md` and generates the artifact.
2. `evaluator`: A test script or validation agent that strictly compares the generated artifact against `spec.md`.
3. `runner`: A script to loop the generator and evaluator (up to N times), halting on success or escalating on max retries.

### Phase 3: Execute and Adjust

1. Instruct the user on how to run the harness. 
2. If the harness fails or produces undesirable results, do not manually edit the generated artifact!
3. Instead, work with the user to update the `spec.md` or improve the evaluator script to catch the problem automatically, then run the harness again.