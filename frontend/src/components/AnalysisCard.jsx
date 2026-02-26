import React from 'react'

export const AnalysisCard = ({ data }) => {
    if (!data) return null

    const { summary, topics, market_impact, sector_impacts } = data

    const getImpactColor = (impact) => {
        const lower = impact?.toLowerCase() || ''
        if (lower.includes('bullish') || lower.includes('positive')) return 'text-emerald-700 bg-emerald-50 border-emerald-200'
        if (lower.includes('bearish') || lower.includes('negative')) return 'text-rose-700 bg-rose-50 border-rose-200'
        return 'text-slate-600 bg-slate-50 border-slate-200'
    }

    return (
        <div className="analysis-card mt-2 mb-6 p-5 bg-white rounded-xl border border-slate-200 shadow-sm">
            {/* Header with Market Impact Badge */}
            <div className="flex justify-between items-start mb-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">AI Intelligence</h3>
                {market_impact && (
                    <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase ${getImpactColor(market_impact)}`}>
                        {market_impact}
                    </span>
                )}
            </div>

            {/* Summary */}
            <div className="mb-6">
                <p className="text-slate-800 text-[13px] leading-relaxed font-semibold">
                    {summary}
                </p>
            </div>

            {/* Sections */}
            <div className="space-y-4">

                {/* Topics */}
                {topics && topics.length > 0 && (
                    <div>
                        <h4 className="text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-tight">Key Themes</h4>
                        <div className="flex flex-wrap gap-1.5">
                            {topics.map((t, idx) => (
                                <div key={idx} className="group relative">
                                    <span className="cursor-help px-2 py-1 rounded-md bg-slate-50 border border-slate-200 text-[11px] text-slate-600 font-medium hover:border-slate-400 hover:bg-white transition-all">
                                        {t.topic}
                                    </span>
                                    {t.details && (
                                        <div className="absolute bottom-full left-0 mb-2 w-56 p-2.5 bg-slate-900 text-white text-[11px] rounded-lg shadow-2xl hidden group-hover:block z-20 leading-normal">
                                            {t.details}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Sectors */}
                {sector_impacts && Object.keys(sector_impacts).length > 0 && (
                    <div className="pt-2">
                        <h4 className="text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-tight">Sector Outlook</h4>
                        <div className="grid grid-cols-1 gap-1.5">
                            {Object.entries(sector_impacts).map(([sector, details], idx) => (
                                <div key={idx} className="flex justify-between items-center p-2 rounded-lg bg-slate-50/50 border border-slate-100">
                                    <span className="text-[12px] text-slate-700 font-medium">{sector}</span>
                                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase border ${getImpactColor(details.impact)}`}>
                                        {details.impact}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
