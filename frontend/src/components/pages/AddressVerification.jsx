import React, { useState, useContext } from "react";
import { VerificationContext } from "../../contexts/VerificationContext";
import {
	Card,
	CardHeader,
	CardTitle,
	CardDescription,
	CardContent,
} from "../ui/card";
import { Label } from "../ui/label";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Progress } from "../ui/progress";
import {
	Shield,
	Search,
	MapPin,
	Check,
	X,
	RefreshCw,
	BarChart3,
} from "lucide-react";
import { toast } from "sonner";
import Skeleton from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";

// This is the CORRECTED version

const formatVerifierResponse = (backendData) => {
	const score = backendData.confidence_score / 100.0;
	const breakdown = (backendData.findings || []).map((finding) => ({
		source: `${finding.source}: ${finding.note}`,
		match: !finding.note.toLowerCase().includes("no match"),
	}));

	return {
		id: backendData.id, // <-- THIS LINE IS CRITICAL
		address: backendData.address,
		confidence: score,
		breakdown: breakdown,
	};
};

const AddressVerification = () => {
	const [webhookUrl, setWebhookUrl] = useState("");
	const [companyName, setCompanyName] = useState("");
	const [address, setAddress] = useState("");
	const [loading, setLoading] = useState(false);
	const [result, setResult] = useState(null);
	const { addVerification } = useContext(VerificationContext);

	const handleVerify = async () => {
		if (!companyName || !address) {
			toast.error("Please enter both a company name and an address.");
			return;
		}
		setLoading(true);
		setResult(null);

		try {
			const response = await fetch("http://127.0.0.1:5000/api/verify", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				// --- 2. ADD THE WEBHOOK URL TO THE REQUEST ---
				body: JSON.stringify({
					company_name: companyName,
					address: address,
					webhook_url: webhookUrl,
				}),
			});

			if (!response.ok) throw new Error("Network response was not ok");

			const backendData = await response.json();
			const formattedData = formatVerifierResponse(backendData);
			setResult(formattedData);
			addVerification(formattedData);
			toast.success("Verification complete!");
		} catch (error) {
			// ... (error handling)
		} finally {
			setLoading(false);
		}
	};

	const getConfidenceColor = (score) => {
		if (score > 0.8) return "text-green-500";
		if (score > 0.4) return "text-amber-500";
		return "text-red-500";
	};

	const getProgressColor = (score) => {
		if (score > 0.8) return "[&>*]:bg-green-500";
		if (score > 0.4) return "[&>*]:bg-amber-500";
		return "[&>*]:bg-red-500";
	};

	return (
		<div className="space-y-8 px-2 md:px-4 py-4 max-w-4xl mx-auto">
			<div>
				<h1 className="text-3xl font-extrabold mb-1">
					Single Address Verification
				</h1>
				<p className="text-muted-foreground text-base">
					Verify a company at an address using our multi-source engine.
				</p>
			</div>
			<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
				{/* Input Card */}
				<Card className="shadow-lg rounded-xl">
					<CardHeader>
						<CardTitle className="flex items-center gap-2">
							<Search className="h-5 w-5" />
							Verification Input
						</CardTitle>
						<CardDescription>
							Enter the company and address you want to check.
						</CardDescription>
					</CardHeader>
					<CardContent className="space-y-5">
						<div className="space-y-3">
							<Label htmlFor="company-name">Company Name</Label>
							<Input
								id="company-name"
								placeholder="e.g., Google LLC"
								value={companyName}
								onChange={(e) => setCompanyName(e.target.value)}
								disabled={loading}
							/>
						</div>

						<div className="space-y-3">
							<Label htmlFor="address">Full Address</Label>
							<Input
								id="address"
								placeholder="e.g., 1600 Amphitheatre Parkway, Mountain View, CA"
								value={address}
								onChange={(e) => setAddress(e.target.value)}
								disabled={loading}
							/>
						</div>
						<div className="space-y-2">
							<Label htmlFor="webhook-url">Webhook URL (Optional)</Label>
							<Input
								id="webhook-url"
								placeholder="https://webhook.site/..."
								value={webhookUrl}
								onChange={(e) => setWebhookUrl(e.target.value)}
							/>
						</div>

						<Button
							onClick={handleVerify}
							disabled={loading}
							className="w-full mt-2"
						>
							{loading ? (
								<RefreshCw className="mr-2 h-4 w-4 animate-spin" />
							) : (
								<Shield className="mr-2 h-4 w-4" />
							)}
							{loading ? "Verifying..." : "Verify Address"}
						</Button>
					</CardContent>
				</Card>

				{/* Result Card */}
				<Card className="flex flex-col shadow-lg rounded-xl min-h-[320px]">
					<CardHeader>
						<CardTitle className="flex items-center gap-2">
							<BarChart3 className="h-5 w-5" />
							Verification Result
						</CardTitle>
						<CardDescription>
							Detailed analysis from our data sources.
						</CardDescription>
					</CardHeader>
					<CardContent className="flex-grow flex items-center justify-center">
						{/* State 1: Initial Placeholder */}
						{!result && !loading && (
							<div className="text-center text-muted-foreground py-8">
								<MapPin className="mx-auto h-12 w-12 opacity-60" />
								<p className="mt-2">Results will be displayed here.</p>
							</div>
						)}

						{/* State 2: Loading (Skeleton for smoother feel) */}
						{loading && (
							<div className="w-full space-y-6">
								<div className="text-center border rounded-lg p-6">
									<h3 className="text-sm font-medium text-muted-foreground mb-2">
										Confidence Score
									</h3>
									<Skeleton
										height={50}
										width={90}
										style={{ margin: "0 auto" }}
									/>
									<Skeleton height={12} width="100%" className="mt-2" />
								</div>
								<div>
									<h4 className="font-semibold mb-2">
										<Skeleton width={150} />
									</h4>
									<div className="space-y-2">
										<Skeleton height={45} />
										<Skeleton height={45} />
									</div>
								</div>
							</div>
						)}

						{/* State 3: Display Results */}
						{result && !loading && (
							<div className="w-full space-y-6">
								<div className="text-center border rounded-lg p-6 bg-muted/40">
									<h3 className="text-sm font-medium text-muted-foreground mb-2">
										Confidence Score
									</h3>
									<p
										className={`text-6xl font-bold ${getConfidenceColor(
											result.confidence
										)}`}
									>
										{(result.confidence * 100).toFixed(0)}
									</p>
									<Progress
										value={result.confidence * 100}
										className={`h-2 mt-2 transition-all duration-300 ease-in ${getProgressColor(
											result.confidence
										)}`}
									/>
								</div>
								<div>
									<h4 className="font-semibold mb-2">Score Breakdown</h4>
									<div className="space-y-2">
										{result.breakdown.map((item, index) => (
											<div
												key={index}
												className="flex justify-between items-center p-3 rounded-md bg-secondary/70"
											>
												<p className="text-sm font-medium">{item.source}</p>
												{item.match ? (
													<div className="flex items-center text-green-600">
														<Check className="h-4 w-4 mr-1" />
														<span className="text-sm">Match</span>
													</div>
												) : (
													<div className="flex items-center text-red-600">
														<X className="h-4 w-4 mr-1" />
														<span className="text-sm">Mismatch</span>
													</div>
												)}
											</div>
										))}
									</div>
								</div>
								<Button
									variant="outline"
									className="w-full mt-4"
									// Add a disabled check to prevent clicking with no ID
									disabled={!result.id}
									onClick={() =>
										window.open(
											`http://127.0.0.1:5000/api/get-report/${result.id}`
										)
									}
								>
									{result.id ? "Download Report" : "Report Unavailable"}
								</Button>
							</div>
						)}
					</CardContent>
				</Card>
			</div>
		</div>
	);
};

export default AddressVerification;
