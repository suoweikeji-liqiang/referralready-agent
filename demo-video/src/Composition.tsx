import React from "react";
import {
	AbsoluteFill,
	Easing,
	Img,
	Sequence,
	interpolate,
	spring,
	staticFile,
	useCurrentFrame,
	useVideoConfig,
} from "remotion";

const colors = {
	bg: "#f5fbfd",
	ink: "#163243",
	muted: "#537183",
	teal: "#11839a",
	tealDark: "#0a5f72",
	blue: "#1654a5",
	green: "#34b57a",
	line: "#cfe2ea",
	panel: "#ffffff",
	panelSoft: "#eef7fb",
};

const scenePadding = 84;

const fadeInUp = (frame: number, fps: number, delay = 0, duration = 20) => {
	const progress = spring({
		fps,
		frame: frame - delay,
		config: {
			damping: 200,
			stiffness: 120,
			mass: 0.7,
		},
		durationInFrames: duration,
	});

	return {
		opacity: progress,
		transform: `translateY(${interpolate(progress, [0, 1], [24, 0])}px)`,
	};
};

const SectionTitle: React.FC<{eyebrow: string; title: string; subtitle: string}> = ({
	eyebrow,
	title,
	subtitle,
}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	return (
		<div
			style={{
				display: "flex",
				flexDirection: "column",
				gap: 12,
				...fadeInUp(frame, fps, 0, 24),
			}}
		>
			<div
				style={{
					fontSize: 20,
					letterSpacing: 2.6,
					textTransform: "uppercase",
					fontWeight: 700,
					color: colors.teal,
				}}
			>
				{eyebrow}
			</div>
			<div
				style={{
					fontSize: 58,
					lineHeight: 1.04,
					fontWeight: 800,
					color: colors.ink,
					maxWidth: 980,
				}}
			>
				{title}
			</div>
			<div
				style={{
					fontSize: 25,
					lineHeight: 1.45,
					color: colors.muted,
					maxWidth: 980,
				}}
			>
				{subtitle}
			</div>
		</div>
	);
};

const Badge: React.FC<{label: string; tone?: "teal" | "green" | "blue"}> = ({
	label,
	tone = "teal",
}) => {
	const palette =
		tone === "green"
			? {bg: "#e9f8f1", fg: "#18764d"}
			: tone === "blue"
				? {bg: "#ebf2fe", fg: "#174f9c"}
				: {bg: "#e7f7fa", fg: colors.tealDark};
	return (
		<div
			style={{
				padding: "10px 16px",
				borderRadius: 999,
				backgroundColor: palette.bg,
				color: palette.fg,
				fontSize: 18,
				fontWeight: 700,
				display: "inline-flex",
			}}
		>
			{label}
		</div>
	);
};

const Card: React.FC<{
	children: React.ReactNode;
	style?: React.CSSProperties;
}> = ({children, style}) => {
	return (
		<div
			style={{
				backgroundColor: colors.panel,
				border: `1px solid ${colors.line}`,
				borderRadius: 28,
				boxShadow: "0 20px 50px rgba(16, 54, 79, 0.08)",
				padding: 28,
				...style,
			}}
		>
			{children}
		</div>
	);
};

const GridBackground: React.FC = () => {
	const frame = useCurrentFrame();
	const {durationInFrames} = useVideoConfig();
	const progress = frame / durationInFrames;
	return (
		<>
			<AbsoluteFill
				style={{
					background:
						"radial-gradient(circle at top right, rgba(17,131,154,0.14), transparent 28%), radial-gradient(circle at bottom left, rgba(22,84,165,0.12), transparent 30%), linear-gradient(180deg, #f8fdff 0%, #eff7fb 100%)",
				}}
			/>
			<AbsoluteFill
				style={{
					backgroundImage:
						"linear-gradient(rgba(17,131,154,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(17,131,154,0.06) 1px, transparent 1px)",
					backgroundSize: "64px 64px",
					opacity: interpolate(progress, [0, 1], [0.3, 0.14]),
				}}
			/>
		</>
	);
};

const TitleScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return (
		<AbsoluteFill style={{padding: scenePadding}}>
			<GridBackground />
			<div
				style={{
					display: "flex",
					flex: 1,
					alignItems: "center",
					justifyContent: "space-between",
					gap: 48,
				}}
			>
				<div style={{flex: 1, display: "flex", flexDirection: "column", gap: 28}}>
					<SectionTitle
						eyebrow="Agents Assemble Demo"
						title="ReferralReady Agent"
						subtitle="An MCP-powered workflow server that turns fragmented synthetic clinical context into specialist-ready referral packets."
					/>
					<div
						style={{
							display: "flex",
							gap: 14,
							flexWrap: "wrap",
							...fadeInUp(frame, fps, 10, 22),
						}}
					>
						<Badge label="Prompt Opinion Marketplace" />
						<Badge label="FHIR Context Enabled" tone="green" />
						<Badge label="Rendered on Render" tone="blue" />
					</div>
				</div>
				<Card
					style={{
						width: 360,
						height: 360,
						display: "flex",
						alignItems: "center",
						justifyContent: "center",
						backgroundColor: "#fbfeff",
						...fadeInUp(frame, fps, 8, 24),
					}}
				>
					<Img
						src={staticFile("assets/referralready-logo.png")}
						style={{
							width: 240,
							height: 240,
							objectFit: "contain",
						}}
					/>
				</Card>
			</div>
		</AbsoluteFill>
	);
};

const ProblemScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const points = [
		"Recent lab trends are missing from the referral packet.",
		"Medication context is unclear or incomplete.",
		"Care teams lose time chasing imaging and encounter notes.",
	];

	return (
		<AbsoluteFill style={{padding: scenePadding}}>
			<GridBackground />
			<SectionTitle
				eyebrow="The workflow problem"
				title="Specialty referrals often stall because the packet is incomplete."
				subtitle="ReferralReady focuses on a narrow, credible workflow: assembling the evidence a specialist team actually needs before the handoff."
			/>
			<div style={{height: 34}} />
			<div style={{display: "flex", gap: 22}}>
				{points.map((point, index) => (
					<Card
						key={point}
						style={{
							flex: 1,
							minHeight: 220,
							display: "flex",
							flexDirection: "column",
							gap: 18,
							...fadeInUp(frame, fps, 10 + index * 8, 24),
						}}
					>
						<div
							style={{
								width: 54,
								height: 54,
								borderRadius: 18,
								backgroundColor: index === 2 ? "#ebf2fe" : "#e7f7fa",
								display: "flex",
								alignItems: "center",
								justifyContent: "center",
								fontSize: 26,
							}}
						>
							{index === 0 ? "🧪" : index === 1 ? "💊" : "📎"}
						</div>
						<div style={{fontSize: 30, fontWeight: 750, lineHeight: 1.25, color: colors.ink}}>{point}</div>
						<div style={{fontSize: 20, lineHeight: 1.45, color: colors.muted}}>
							Human review stays in place, but the packet becomes clearer, faster to route, and safer to interpret.
						</div>
					</Card>
				))}
			</div>
		</AbsoluteFill>
	);
};

const ArchitectureScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const nodeStyle: React.CSSProperties = {
		flex: 1,
		minHeight: 180,
		display: "flex",
		flexDirection: "column",
		gap: 12,
		justifyContent: "center",
		alignItems: "center",
		textAlign: "center",
	};

	return (
		<AbsoluteFill style={{padding: scenePadding}}>
			<GridBackground />
			<SectionTitle
				eyebrow="Architecture"
				title="Prompt Opinion orchestrates the agent. ReferralReady provides the MCP workflow layer."
				subtitle="The deployment is public, the toolchain is deterministic, and FHIR context can now be passed into the MCP server when available."
			/>
			<div style={{height: 34}} />
			<div style={{display: "flex", alignItems: "center", gap: 18}}>
				{[
					{
						title: "Prompt Opinion",
						body: "Marketplace listing, agent runtime, and patient-aware invocation.",
						tone: "teal",
					},
					{
						title: "ReferralReady MCP",
						body: "Six tools for snapshot, signals, completeness, packet generation, and care coordination.",
						tone: "green",
					},
					{
						title: "Render Deployment",
						body: "Public streamable HTTP MCP endpoint with health checks and FHIR extension declaration.",
						tone: "blue",
					},
					{
						title: "FHIR or Local Data",
						body: "Uses Prompt Opinion FHIR context when supplied, with safe synthetic fallback for demos.",
						tone: "teal",
					},
				].map((node, index) => (
					<React.Fragment key={node.title}>
						<Card style={{...nodeStyle, ...fadeInUp(frame, fps, 8 + index * 7, 22)}}>
							<Badge label={node.title} tone={node.tone as "teal" | "green" | "blue"} />
							<div style={{fontSize: 20, lineHeight: 1.45, color: colors.muted, maxWidth: 220}}>{node.body}</div>
						</Card>
						{index < 3 ? (
							<div
								style={{
									fontSize: 42,
									color: colors.teal,
									fontWeight: 700,
									...fadeInUp(frame, fps, 20 + index * 7, 18),
								}}
							>
								→
							</div>
						) : null}
					</React.Fragment>
				))}
			</div>
		</AbsoluteFill>
	);
};

const MarketplaceScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return (
		<AbsoluteFill style={{padding: scenePadding}}>
			<GridBackground />
			<SectionTitle
				eyebrow="Live status"
				title="The MCP server is published and the Prompt Opinion FHIR extension is now recognized."
				subtitle="This is the point where the project becomes competition-ready: public listing, public endpoint, and platform-level FHIR context support."
			/>
			<div style={{height: 34}} />
			<div style={{display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 24}}>
				<Card style={{minHeight: 350, ...fadeInUp(frame, fps, 10, 24)}}>
					<div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
						<div>
							<div style={{fontSize: 18, color: colors.teal, fontWeight: 800, textTransform: "uppercase", letterSpacing: 1.8}}>
								Prompt Opinion Marketplace
							</div>
							<div style={{fontSize: 40, fontWeight: 800, color: colors.ink, marginTop: 8}}>ReferralReady Agent</div>
							<div style={{fontSize: 22, color: colors.muted, marginTop: 10}}>
								Published as an MCP Server listing with six tools.
							</div>
						</div>
						<Badge label="Open Access" tone="green" />
					</div>
					<div style={{height: 22}} />
					<div style={{display: "flex", gap: 14, flexWrap: "wrap"}}>
						<Badge label="MCP Server" tone="blue" />
						<Badge label="Tools (6)" />
						<Badge label="FHIR Context Supported" tone="green" />
					</div>
					<div style={{height: 28}} />
					<div style={{fontSize: 21, lineHeight: 1.6, color: colors.muted}}>
						ReferralReady assembles specialist-ready referral packets from synthetic FHIR-like data, flags missing referral
						information, and generates care coordination tasks for human review.
					</div>
				</Card>
				<div style={{display: "flex", flexDirection: "column", gap: 18}}>
					<Card style={{minHeight: 160, ...fadeInUp(frame, fps, 18, 22)}}>
						<div style={{fontSize: 18, fontWeight: 800, color: colors.teal, textTransform: "uppercase", letterSpacing: 1.8}}>
							Render health check
						</div>
						<div style={{height: 14}} />
						<div style={{fontSize: 20, lineHeight: 1.65, color: colors.ink}}>
							`/healthz` returns a live public endpoint plus Prompt Opinion FHIR extension metadata.
						</div>
					</Card>
					<Card style={{minHeight: 170, ...fadeInUp(frame, fps, 24, 22)}}>
						<div style={{fontSize: 18, fontWeight: 800, color: colors.teal, textTransform: "uppercase", letterSpacing: 1.8}}>
							Initialize response
						</div>
						<div style={{height: 14}} />
						<div style={{fontSize: 20, lineHeight: 1.65, color: colors.ink}}>
							The server now declares
							<span style={{fontWeight: 800}}> `ai.promptopinion/fhir-context` </span>
							with patient read scopes in MCP capabilities.
						</div>
					</Card>
				</div>
			</div>
		</AbsoluteFill>
	);
};

const WorkflowScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const tools = [
		"get_patient_snapshot",
		"get_recent_clinical_signals",
		"get_medication_context",
		"check_referral_completeness",
		"build_referral_packet",
	];
	return (
		<AbsoluteFill style={{padding: scenePadding}}>
			<GridBackground />
			<SectionTitle
				eyebrow="Live workflow"
				title="A single prompt triggers a transparent referral packet workflow."
				subtitle="For the competition demo, the workflow uses synthetic patient SYN-CKD-004 and assembles a nephrology packet end to end."
			/>
			<div style={{height: 28}} />
			<div style={{display: "grid", gridTemplateColumns: "1fr 1fr", gap: 22}}>
				<Card style={{minHeight: 410, ...fadeInUp(frame, fps, 6, 24)}}>
					<div style={{fontSize: 18, color: colors.teal, fontWeight: 800, textTransform: "uppercase", letterSpacing: 1.8}}>
						Competition prompt
					</div>
					<div style={{height: 18}} />
					<div
						style={{
							fontSize: 25,
							lineHeight: 1.55,
							color: colors.ink,
							padding: 24,
							borderRadius: 20,
							backgroundColor: colors.panelSoft,
							border: `1px solid ${colors.line}`,
						}}
					>
						Prepare a nephrology referral packet for synthetic patient <b>SYN-CKD-004</b>. Include the referral rationale,
						key clinical evidence, missing information before referral, and care coordinator tasks. Do not diagnose or
						recommend treatment.
					</div>
					<div style={{height: 18}} />
					<div style={{display: "flex", gap: 10, flexWrap: "wrap"}}>
						<Badge label="Workspace + Patient context" tone="blue" />
						<Badge label="FHIR extension enabled" tone="green" />
					</div>
				</Card>
				<Card style={{minHeight: 410, ...fadeInUp(frame, fps, 12, 24)}}>
					<div style={{fontSize: 18, color: colors.teal, fontWeight: 800, textTransform: "uppercase", letterSpacing: 1.8}}>
						Tool sequence
					</div>
					<div style={{height: 18}} />
					<div style={{display: "flex", flexDirection: "column", gap: 14}}>
						{tools.map((tool, index) => (
							<div
								key={tool}
								style={{
									padding: "16px 18px",
									borderRadius: 18,
									backgroundColor: "#f8fbfc",
									border: `1px solid ${colors.line}`,
									fontSize: 22,
									fontWeight: 700,
									color: colors.ink,
									...fadeInUp(frame, fps, 18 + index * 8, 18),
								}}
							>
								{tool}
							</div>
						))}
					</div>
				</Card>
			</div>
		</AbsoluteFill>
	);
};

const OutputScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return (
		<AbsoluteFill style={{padding: scenePadding}}>
			<GridBackground />
			<SectionTitle
				eyebrow="Output"
				title="The packet is readable, structured, and explicit about safety."
				subtitle="The result highlights the referral rationale, evidence, completeness status, and a clear human-review boundary."
			/>
			<div style={{height: 30}} />
			<Card style={{minHeight: 410, ...fadeInUp(frame, fps, 8, 24)}}>
				<div style={{display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 30}}>
					<div style={{display: "flex", flexDirection: "column", gap: 16}}>
						<div style={{fontSize: 36, fontWeight: 800, color: colors.ink}}>Nephrology Referral Packet</div>
						<div style={{fontSize: 22, lineHeight: 1.55, color: colors.muted}}>
							Synthetic patient <b>SYN-CKD-004</b> with progressive CKD review, complete referral checklist, and ready-to-route
							packet.
						</div>
						<div style={{height: 8}} />
						<div style={{fontSize: 22, fontWeight: 800, color: colors.ink}}>Key evidence</div>
						<div style={{fontSize: 22, color: colors.ink, lineHeight: 1.7}}>
							• eGFR: <b>58 → 52 mL/min/1.73m²</b>
							<br />• Creatinine: <b>1.2 → 1.4 mg/dL</b>
							<br />• UACR: <b>86 mg/g</b>
							<br />• Renal ultrasound attached
							<br />• Checklist completeness: <b>100%</b>
						</div>
					</div>
					<div
						style={{
							padding: 24,
							borderRadius: 22,
							backgroundColor: "#f8fbfc",
							border: `1px solid ${colors.line}`,
							display: "flex",
							flexDirection: "column",
							justifyContent: "space-between",
						}}
					>
						<div>
							<div style={{fontSize: 20, fontWeight: 800, color: colors.teal, textTransform: "uppercase", letterSpacing: 1.8}}>
								Safety boundary
							</div>
							<div style={{height: 14}} />
							<div style={{fontSize: 24, lineHeight: 1.6, color: colors.ink}}>
								Synthetic data only.
								<br />
								No diagnosis.
								<br />
								No treatment recommendation.
								<br />
								Human review required.
							</div>
						</div>
						<div style={{display: "flex", gap: 12, flexWrap: "wrap"}}>
							<Badge label="Synthetic only" tone="green" />
							<Badge label="Workflow support" tone="blue" />
						</div>
					</div>
				</div>
			</Card>
		</AbsoluteFill>
	);
};

const ClosingScene: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return (
		<AbsoluteFill style={{padding: scenePadding}}>
			<GridBackground />
			<div
				style={{
					display: "flex",
					flex: 1,
					alignItems: "center",
					justifyContent: "space-between",
					gap: 32,
				}}
			>
				<div style={{flex: 1, display: "flex", flexDirection: "column", gap: 22}}>
					<SectionTitle
						eyebrow="Closing"
						title="ReferralReady Agent"
						subtitle="FHIR-aware referral packet generation for safer specialist handoffs."
					/>
					<div style={{display: "flex", flexDirection: "column", gap: 10, ...fadeInUp(frame, fps, 12, 22)}}>
						<div style={{fontSize: 22, color: colors.ink}}>
							Prompt Opinion Marketplace
						</div>
						<div style={{fontSize: 20, color: colors.muted}}>app.promptopinion.ai/marketplace/mcp/...</div>
						<div style={{fontSize: 22, color: colors.ink, marginTop: 8}}>Public MCP endpoint</div>
						<div style={{fontSize: 20, color: colors.muted}}>referralready-agent.onrender.com/mcp</div>
					</div>
				</div>
				<Card
					style={{
						width: 320,
						height: 320,
						display: "flex",
						alignItems: "center",
						justifyContent: "center",
						backgroundColor: "#fbfeff",
						...fadeInUp(frame, fps, 8, 24),
					}}
				>
					<Img
						src={staticFile("assets/referralready-logo.png")}
						style={{
							width: 210,
							height: 210,
							objectFit: "contain",
						}}
					/>
				</Card>
			</div>
		</AbsoluteFill>
	);
};

export const ReferralReadyDemo: React.FC = () => {
	const frame = useCurrentFrame();
	const vignetteOpacity = interpolate(frame, [0, 2160], [0.05, 0.12], {
		extrapolateRight: "clamp",
		easing: Easing.out(Easing.cubic),
	});

	return (
		<AbsoluteFill
			style={{
				fontFamily:
					'"Segoe UI", "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif',
				color: colors.ink,
				backgroundColor: colors.bg,
			}}
		>
			<AbsoluteFill
				style={{
					background:
						"radial-gradient(circle at center, transparent 48%, rgba(22,50,67,0.08) 100%)",
					opacity: vignetteOpacity,
				}}
			/>
			<Sequence durationInFrames={180}>
				<TitleScene />
			</Sequence>
			<Sequence from={180} durationInFrames={300}>
				<ProblemScene />
			</Sequence>
			<Sequence from={480} durationInFrames={330}>
				<ArchitectureScene />
			</Sequence>
			<Sequence from={810} durationInFrames={360}>
				<MarketplaceScene />
			</Sequence>
			<Sequence from={1170} durationInFrames={510}>
				<WorkflowScene />
			</Sequence>
			<Sequence from={1680} durationInFrames={330}>
				<OutputScene />
			</Sequence>
			<Sequence from={2010} durationInFrames={150}>
				<ClosingScene />
			</Sequence>
			<div
				style={{
					position: "absolute",
					left: 48,
					bottom: 30,
					fontSize: 16,
					letterSpacing: 1.4,
					textTransform: "uppercase",
					color: "rgba(22, 50, 67, 0.55)",
				}}
			>
				Agents Assemble • English-only competition demo
			</div>
		</AbsoluteFill>
	);
};
