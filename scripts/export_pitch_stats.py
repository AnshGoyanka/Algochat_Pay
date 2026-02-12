"""
Pitch Statistics Exporter
Export demo metrics in presentation-ready formats
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import csv
from datetime import datetime
from typing import List, Dict, Any

from backend.database import SessionLocal
from backend.services.demo_metrics_service import DemoMetricsService
from scripts.demo_playback import DemoTimelinePlayback


class PitchStatsExporter:
    """
    Export demo statistics for pitch decks and presentations
    """
    
    def __init__(self, db):
        self.db = db
        self.metrics = DemoMetricsService(db)
        self.timeline = DemoTimelinePlayback(db)
        self.export_dir = Path("data/pitch_exports")
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_keynote_stats(self) -> str:
        """
        Export key statistics in markdown format
        Perfect for copy-paste into presentation slides
        """
        comprehensive = self.metrics.get_comprehensive_demo_metrics()
        talking_points = self.metrics.get_judge_talking_points()
        
        wallets = comprehensive['wallets']
        txs = comprehensive['transactions']
        volume = comprehensive['volume']
        settlement = comprehensive['settlement']
        fundraising = comprehensive['fundraising']
        tickets = comprehensive['tickets']
        
        md = "# AlgoChat Pay - Pitch Statistics\n\n"
        md += f"_Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_\n\n"
        md += "---\n\n"
        
        md += "## 🎯 Key Metrics (For Title Slides)\n\n"
        md += f"### User Adoption\n"
        md += f"- **{wallets['total_wallets']}** students onboarded\n"
        md += f"- **{wallets['activation_rate']}%** activation rate\n"
        md += f"- **{wallets['weekly_active_users']}** weekly active users\n\n"
        
        md += f"### Transaction Performance\n"
        md += f"- **{txs['overall_success_rate']}%** success rate\n"
        md += f"- **{settlement['average_seconds']}s** average settlement\n"
        md += f"- **{txs['total_transactions']:,}** total transactions\n\n"
        
        md += f"### Financial Volume\n"
        md += f"- **{volume['total_volume_algo']:,.2f} ALGO** total volume\n"
        md += f"- **{volume['average_transaction_algo']:.2f} ALGO** average transaction\n"
        md += f"- **{volume['week_volume_algo']:,.2f} ALGO** this week\n\n"
        
        md += f"### Impact\n"
        md += f"- **{fundraising['total_campaigns']}** fundraising campaigns\n"
        md += f"- **{fundraising['total_raised_algo']:,.2f} ALGO** raised for campus causes\n"
        md += f"- **{tickets['total_tickets_minted']}** NFT tickets minted\n"
        md += f"- **{tickets['unique_events']}** campus events powered\n\n"
        
        md += "---\n\n"
        md += "## 💬 Judge Talking Points\n\n"
        for i, point in enumerate(talking_points, 1):
            md += f"{i}. {point}\n"
        
        md += "\n---\n\n"
        md += "## 📊 Quick Copy-Paste Stats\n\n"
        md += "```\n"
        md += f"{wallets['total_wallets']} Students | "
        md += f"{txs['overall_success_rate']}% Success Rate | "
        md += f"{settlement['average_seconds']}s Settlement | "
        md += f"{volume['total_volume_algo']:,.0f} ALGO Volume\n"
        md += "```\n\n"
        
        output_file = self.export_dir / "keynote_stats.md"
        with open(output_file, 'w') as f:
            f.write(md)
        
        return str(output_file)
    
    def export_csv_metrics(self) -> str:
        """
        Export comprehensive metrics as CSV
        Perfect for importing into Excel/Google Sheets
        """
        comprehensive = self.metrics.get_comprehensive_demo_metrics()
        
        # Flatten the nested dict into rows
        rows = []
        
        # Add wallet metrics
        for key, value in comprehensive['wallets'].items():
            rows.append({
                'category': 'Wallets',
                'metric': key.replace('_', ' ').title(),
                'value': value,
                'unit': '%' if 'rate' in key else 'count'
            })
        
        # Add transaction metrics
        for key, value in comprehensive['transactions'].items():
            rows.append({
                'category': 'Transactions',
                'metric': key.replace('_', ' ').title(),
                'value': value,
                'unit': '%' if 'rate' in key else 'count'
            })
        
        # Add volume metrics
        for key, value in comprehensive['volume'].items():
            unit = 'ALGO' if 'algo' in key else 'count'
            rows.append({
                'category': 'Volume',
                'metric': key.replace('_', ' ').title(),
                'value': value,
                'unit': unit
            })
        
        # Add settlement metrics
        for key, value in comprehensive['settlement'].items():
            unit = 'seconds' if 'seconds' in key else 'count'
            rows.append({
                'category': 'Settlement',
                'metric': key.replace('_', ' ').title(),
                'value': value,
                'unit': unit
            })
        
        # Add fundraising metrics
        for key, value in comprehensive['fundraising'].items():
            unit = 'ALGO' if 'algo' in key else '%' if 'rate' in key or 'progress' in key else 'count'
            rows.append({
                'category': 'Fundraising',
                'metric': key.replace('_', ' ').title(),
                'value': value,
                'unit': unit
            })
        
        # Add ticket metrics
        for key, value in comprehensive['tickets'].items():
            unit = 'ALGO' if 'algo' in key or 'price' in key else 'count'
            rows.append({
                'category': 'Tickets',
                'metric': key.replace('_', ' ').title(),
                'value': value,
                'unit': unit
            })
        
        output_file = self.export_dir / "metrics_export.csv"
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['category', 'metric', 'value', 'unit'])
            writer.writeheader()
            writer.writerows(rows)
        
        return str(output_file)
    
    def export_daily_trends_csv(self) -> str:
        """
        Export daily trends as CSV for charting
        """
        daily_stats = self.metrics.get_daily_transaction_stats(30)  # Last 30 days
        
        output_file = self.export_dir / "daily_trends.csv"
        
        with open(output_file, 'w', newline='') as f:
            if daily_stats:
                writer = csv.DictWriter(f, fieldnames=daily_stats[0].keys())
                writer.writeheader()
                writer.writerows(daily_stats)
        
        return str(output_file)
    
    def export_hourly_pattern_csv(self) -> str:
        """
        Export hourly activity pattern as CSV
        """
        hourly_stats = self.timeline.get_hourly_activity_stats()
        
        output_file = self.export_dir / "hourly_pattern.csv"
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'hour', 'hour_label', 'transactions', 'volume_algo',
                'expected_multiplier', 'activity_level'
            ])
            writer.writeheader()
            writer.writerows(hourly_stats)
        
        return str(output_file)
    
    def export_json_complete(self) -> str:
        """
        Export complete metrics as JSON
        Perfect for web dashboards or API consumers
        """
        comprehensive = self.metrics.get_comprehensive_demo_metrics()
        talking_points = self.metrics.get_judge_talking_points()
        peak_analysis = self.timeline.get_peak_hours_analysis()
        
        export_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "format_version": "1.0",
            "metrics": comprehensive,
            "talking_points": talking_points,
            "peak_hours_analysis": peak_analysis
        }
        
        output_file = self.export_dir / "complete_metrics.json"
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return str(output_file)
    
    def export_presentation_slides_text(self) -> str:
        """
        Export presentation-ready text snippets
        """
        comprehensive = self.metrics.get_comprehensive_demo_metrics()
        
        wallets = comprehensive['wallets']
        txs = comprehensive['transactions']
        volume = comprehensive['volume']
        settlement = comprehensive['settlement']
        fundraising = comprehensive['fundraising']
        tickets = comprehensive['tickets']
        
        slides = "# AlgoChat Pay - Presentation Slides Text\n\n"
        slides += "## Slide 1: Problem\n"
        slides += "**Title:** Campus Payments Are Broken\n\n"
        slides += "**Body:**\n"
        slides += "- Cash-only vendors limit student access\n"
        slides += "- Traditional payment apps have high fees\n"
        slides += "- No unified system for payments, tickets, fundraising\n"
        slides += "- Students want simple, fast, secure transactions\n\n"
        
        slides += "---\n\n"
        slides += "## Slide 2: Solution\n"
        slides += "**Title:** WhatsApp + Algorand = Campus Wallet\n\n"
        slides += "**Body:**\n"
        slides += "- No app download - works via WhatsApp\n"
        slides += f"- {settlement['average_seconds']}s blockchain settlement\n"
        slides += "- Zero knowledge required - just text to pay\n"
        slides += "- Multi-use: Payments + Tickets + Fundraising\n\n"
        
        slides += "---\n\n"
        slides += "## Slide 3: Traction\n"
        slides += "**Title:** Already Adopted Across Campus\n\n"
        slides += "**Body:**\n"
        slides += f"- {wallets['total_wallets']} students onboarded\n"
        slides += f"- {wallets['activation_rate']}% activation rate\n"
        slides += f"- {txs['total_transactions']:,} transactions completed\n"
        slides += f"- {volume['total_volume_algo']:,.0f} ALGO transacted\n\n"
        
        slides += "---\n\n"
        slides += "## Slide 4: Technical Excellence\n"
        slides += "**Title:** Production-Grade Architecture\n\n"
        slides += "**Body:**\n"
        slides += f"- {txs['overall_success_rate']}% transaction success rate\n"
        slides += f"- {settlement['average_seconds']}s average blockchain confirmation\n"
        slides += "- Algorand smart contracts (PyTeal)\n"
        slides += "- Security: Rate limiting, audit logs, encryption\n\n"
        
        slides += "---\n\n"
        slides += "## Slide 5: Impact\n"
        slides += "**Title:** Real Campus Impact\n\n"
        slides += "**Body:**\n"
        slides += f"- {fundraising['successful_campaigns']} fundraising campaigns succeeded\n"
        slides += f"- {fundraising['total_raised_algo']:,.0f} ALGO raised for campus causes\n"
        slides += f"- {tickets['total_tickets_minted']} NFT tickets sold\n"
        slides += f"- {tickets['unique_events']} campus events powered\n\n"
        
        slides += "---\n\n"
        slides += "## Slide 6: The Ask\n"
        slides += "**Title:** Scale to 100 Campuses\n\n"
        slides += "**Body:**\n"
        slides += "- Proven traction on our campus\n"
        slides += "- Seeking partnership to expand\n"
        slides += "- Target: 100,000 students by end of year\n"
        slides += "- Join us in making blockchain payments accessible\n\n"
        
        output_file = self.export_dir / "presentation_slides.md"
        with open(output_file, 'w') as f:
            f.write(slides)
        
        return str(output_file)
    
    def export_all_formats(self):
        """
        Export in all formats at once
        """
        print("\n" + "="*80)
        print("📊 EXPORTING PITCH STATISTICS")
        print("="*80 + "\n")
        
        print("Exporting formats...\n")
        
        # Keynote stats
        keynote_file = self.export_keynote_stats()
        print(f"✅ Keynote Stats: {keynote_file}")
        
        # CSV exports
        csv_file = self.export_csv_metrics()
        print(f"✅ CSV Metrics: {csv_file}")
        
        daily_file = self.export_daily_trends_csv()
        print(f"✅ Daily Trends CSV: {daily_file}")
        
        hourly_file = self.export_hourly_pattern_csv()
        print(f"✅ Hourly Pattern CSV: {hourly_file}")
        
        # JSON export
        json_file = self.export_json_complete()
        print(f"✅ Complete JSON: {json_file}")
        
        # Presentation text
        slides_file = self.export_presentation_slides_text()
        print(f"✅ Presentation Slides: {slides_file}")
        
        print("\n" + "="*80)
        print(f"📁 All exports saved to: {self.export_dir}")
        print("="*80 + "\n")
        
        print("📋 Usage Guide:")
        print("  • keynote_stats.md → Copy key metrics into slides")
        print("  • metrics_export.csv → Import into Excel for custom charts")
        print("  • daily_trends.csv → Create trend line charts")
        print("  • hourly_pattern.csv → Visualize campus activity patterns")
        print("  • complete_metrics.json → Full data for web dashboards")
        print("  • presentation_slides.md → Pre-written slide content")
        print()


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export pitch statistics")
    parser.add_argument(
        "format",
        nargs='?',
        choices=["keynote", "csv", "json", "slides", "all"],
        default="all",
        help="Export format (default: all)"
    )
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        exporter = PitchStatsExporter(db)
        
        if args.format == "keynote":
            file = exporter.export_keynote_stats()
            print(f"✅ Exported: {file}")
        
        elif args.format == "csv":
            csv_file = exporter.export_csv_metrics()
            daily_file = exporter.export_daily_trends_csv()
            hourly_file = exporter.export_hourly_pattern_csv()
            print(f"✅ Exported CSV files:")
            print(f"   - {csv_file}")
            print(f"   - {daily_file}")
            print(f"   - {hourly_file}")
        
        elif args.format == "json":
            file = exporter.export_json_complete()
            print(f"✅ Exported: {file}")
        
        elif args.format == "slides":
            file = exporter.export_presentation_slides_text()
            print(f"✅ Exported: {file}")
        
        else:  # all
            exporter.export_all_formats()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
