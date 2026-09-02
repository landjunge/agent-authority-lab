let meta = #{
    name: "agent-authority-lab",
    description: "Verify Agent Authority Lab v0.2 against the frozen composition-gate spec",
    when_to_use: "After changing lab/ or tests/, or before a v0.3 GO/STOP",
    phases: [
        #{ title: "Scope", detail: "confirm frozen spec and intended layout" },
        #{ title: "Review", detail: "invariants, validator, tests in parallel" },
        #{ title: "Verify", detail: "adversarial check that tests were not weakened" },
        #{ title: "Decide", detail: "GO or STOP for v0.3" },
        #{ title: "Push", detail: "git push -u origin HEAD — local-only commits are not done" },
    ],
};

let review_schema = #{
    "type": "object",
    "required": ["ok", "issues"],
    "properties": #{
        "ok": #{ "type": "boolean" },
        "issues": #{
            "type": "array",
            "maxItems": 8,
            "items": #{ "type": "string" },
        },
    },
};

let verdict_schema = #{
    "type": "object",
    "required": ["proceed", "reason"],
    "properties": #{
        "proceed": #{ "type": "boolean" },
        "reason": #{ "type": "string" },
        "blocked": #{ "type": "boolean" },
    },
};

let root = if args == () { () } else { args.root };
if root == () {
    pause("verification", "Pass args.root — path to agent-authority-lab or the frozen spec zip.");
}

phase("Scope");
log("Scoping Agent Authority Lab at " + root);

let scope_prompt = "";
scope_prompt += "You are checking Agent Authority Lab v0.2. Root path: ";
scope_prompt += json_encode(root);
scope_prompt += ". Use read_file, list_dir, and grep only. If the path is a zip, list it with unzip -l via the shell only if needed; prefer reading extracted docs. Confirm these frozen docs exist: README, docs/SPEC-v0.1.md, docs/COMPOSITION-GATE.md, docs/TECH-DECISIONS.md, docs/PROTOTYPE-v0.2.md. Confirm v0.2 forbids real LLMs, real secrets, GitHub API, Biscuit, Cedar, FIDES, and 4AllPass. Return ok=true only if the frozen spec is present and you actually opened the files. issues: short strings for missing or contradictory docs.";

let scoped = agent(scope_prompt, #{
    label: "scope-spec",
    capability_mode: "read-only",
    output_schema: review_schema,
});

if scoped == () || !scoped.success {
    complete(#{ summary: "Scope agent failed.", proceed: false, issues: ["scope-failed"] });
}

phase("Review");
let jobs = [];
jobs.push(#{
    prompt: "Read the Agent Authority Lab tree at " + json_encode(root) + " with read_file/grep. Frozen invariants from docs/PROTOTYPE-v0.2.md: I1 action_count<=100, I2 unique_files_changed<=10, I3 protected path config/security-policy.json immutable, I4 delegation_depth<=1 (document 0 vs 1 convention), I5 no external network destinations, I6 irreversible actions need approval token. Check lab/invariants.py and lab/validator.py if present. ok=true only if all six are encoded and denied requests do not mutate state. issues: concrete missing checks. Empty issues only after reading the files.",
    label: "review-invariants",
    capability_mode: "read-only",
    output_schema: review_schema,
});
jobs.push(#{
    prompt: "Read the Agent Authority Lab tree at " + json_encode(root) + ". Check the validator algorithm: ActionRequest -> predict next WorkflowState -> evaluate invariants -> ALLOW or DENY+reason -> on ALLOW only commit state and provenance. No LLM in the trusted path. Denied requests must not alter state. Use read_file/grep on lab/validator.py lab/state.py lab/provenance.py lab/models.py. ok=true only with evidence from those files (or ok=false with issues if they do not exist yet). Do not invent files.",
    label: "review-validator",
    capability_mode: "read-only",
    output_schema: review_schema,
});
jobs.push(#{
    prompt: "Read tests/ under " + json_encode(root) + " with read_file. Frozen required tests: budget_split (deny action 101), file_limit (deny 11th unique file), protected_paths, delegation_depth, irreversible_gate, cross_agent_accumulation, slow_drift, legitimate_workflow. Tests must not be weakened to fit an implementation. ok=true only if all eight exist and assert the frozen deny/allow boundaries. issues: missing tests or softened assertions. If the tree is spec-only with no tests/ yet, ok=false and list the eight missing test files.",
    label: "review-tests",
    capability_mode: "read-only",
    output_schema: review_schema,
});
let results = parallel(jobs);

let issues = [];
let i = 0;
for r in results {
    if r == () || !r.success {
        issues.push("review-slot-failed:" + i.to_string());
    } else {
        if r.output.ok != true {
            if type_of(r.output.issues) == "array" {
                for item in r.output.issues { issues.push(item); }
            } else {
                issues.push("review-not-ok:" + i.to_string());
            }
        }
    }
    i += 1;
}

phase("Verify");
let verify_prompt = "";
verify_prompt += "Adversarially verify Agent Authority Lab at ";
verify_prompt += json_encode(root);
verify_prompt += ". Fail closed. Set proceed=true only if: (1) all eight frozen v0.2 tests exist and were not weakened, (2) no security decision depends on an LLM, (3) denied requests do not mutate workflow state, (4) provenance has no fake secrets. If this is still spec-only with no implementation, proceed=false and reason must say STOP until the deterministic prototype exists. Read the files; do not answer from memory. blocked=true if evidence is missing.";
let verified = agent(verify_prompt, #{
    label: "verify-go-stop",
    capability_mode: "read-only",
    output_schema: verdict_schema,
});

phase("Decide");
let proceed = false;
let reason = "verifier-failed";
if verified != () && verified.success && verified.output.reason != () {
    reason = verified.output.reason;
    if verified.output.proceed == true && verified.output.blocked != true && issues.len() == 0 {
        proceed = true;
    }
}

phase("Push");
let push_prompt = "";
push_prompt += "Repository root: ";
push_prompt += json_encode(root);
push_prompt += ". This step is mandatory. Run: git -C <root> status -sb ; git -C <root> rev-parse --abbrev-ref HEAD ; git -C <root> push -u origin HEAD. If the branch has no upstream, still push -u origin HEAD. If everything is already up to date, that is success. Never leave commits only local. Do not skip because the rest of this workflow was read-only. Report the remote tracking SHA. SKIP_POST_COMMIT_PUSH is not an excuse here.";
let pushed = agent(push_prompt, #{
    label: "push-origin",
    capability_mode: "execute",
});
let pushed_ok = pushed != () && pushed.success;

let summary = "STOP";
if proceed { summary = "GO"; }
if !pushed_ok { summary = summary + " (push failed — commits may be local only)"; }
log(summary + " — issues=" + issues.len().to_string());
complete(#{
    summary: summary,
    proceed: proceed,
    reason: reason,
    issues: issues,
    root: root,
    pushed: pushed_ok,
});
