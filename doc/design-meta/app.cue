package flyb

source: "astraeawave-design-meta"
name:   "astraeawave-design"
modules: ["design"]

reports: [{
	title:       "AstraeaWave Design"
	filepath:    "../design/design.md"
	description: "Proposed specification assembled from the CSV sources in doc/design-meta/examples; open questions and recommended defaults remain subject to implementation decisions."
	sections: [{
		title: "00 Source Navigation"
		sections: [{
			title: "Concept Registry and Search Convention"
			notes: ["design.concepts", "design.search"]
		}]
	}, {
		title: "01 Functional and Technical Specification"
		sections: [{
			title: "Features, Scope, and Open Questions"
			notes: ["design.features"]
		}]
	}, {
		title: "02 Command-Line Interface"
		sections: [{
			title: "Recommended Commands and Container Workflows"
			notes: ["design.cli"]
		}]
	}, {
		title: "03 Optional Network Faults"
		sections: [{
			title: "Toxiproxy Profiles"
			notes: ["design.network.profiles"]
		}]
	}, {
		title: "04 Technology Choices"
		sections: [{
			title: "Runtime, Libraries, and Tooling"
			notes: ["design.technologies"]
		}]
	}]
}]

notes: [{
	name:      "design.concepts"
	title:     "Canonical Concept Registry"
	filepath:  "examples/concepts.csv"
	arguments: ["format-csv=table"]
	labels: ["concept", "csv"]
}, {
	name:     "design.search"
	title:    "Selective Source Retrieval"
	markdown: "Use the canonical registry to select a primary concept, then search its quoted value across the source catalogs. See the [source search convention](../design-meta/README.md) for rg and grep commands, secondary-topic retrieval, CSV editing rules, and validated regeneration."
	labels: ["documentation", "search"]
}, {
	name:      "design.cli"
	title:     "CLI Command Catalog"
	filepath:  "examples/cli-command.csv"
	arguments: ["format-csv=table"]
	labels: ["cli", "csv"]
}, {
	name:      "design.features"
	title:     "Feature Catalog"
	filepath:  "examples/feature.csv"
	arguments: ["format-csv=table"]
	labels: ["csv", "feature"]
}, {
	name:      "design.network.profiles"
	title:     "Network Profile Catalog"
	filepath:  "examples/network-profile.csv"
	arguments: ["format-csv=table"]
	labels: ["csv", "network"]
}, {
	name:      "design.technologies"
	title:     "Technology Catalog"
	filepath:  "examples/technology.csv"
	arguments: ["format-csv=table"]
	labels: ["csv", "technology"]
}]

relationships: []

argumentRegistry: {
	version: "1"
	arguments: [{
		name:          "format-csv"
		valueType:     "enum"
		scopes: ["note"]
		allowedValues: ["table", "raw"]
	}]
}
