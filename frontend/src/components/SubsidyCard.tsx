import React from 'react';
import type { Subsidy } from '../types';

interface SubsidyCardProps {
  subsidy: Subsidy;
  onDetailClick?: (subsidyId: string) => void;
}

export default function SubsidyCard({ subsidy, onDetailClick }: SubsidyCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-5 mb-4 border border-gray-200 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-bold text-gray-900 flex-1 mr-4">
          {subsidy.title || subsidy.name}
        </h3>
        {subsidy.subsidy_max_limit && (
          <span className="bg-primary-100 text-primary-700 text-sm font-semibold px-3 py-1 rounded-full whitespace-nowrap">
            {subsidy.subsidy_max_limit}
          </span>
        )}
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        {subsidy.target_area && (
          <div className="flex items-start">
            <span className="font-semibold min-w-[80px]">対象地域:</span>
            <span>{subsidy.target_area}</span>
          </div>
        )}

        {subsidy.target_employees && (
          <div className="flex items-start">
            <span className="font-semibold min-w-[80px]">対象従業員:</span>
            <span>{subsidy.target_employees}</span>
          </div>
        )}

        <div className="flex items-start">
          <span className="font-semibold min-w-[80px]">募集期間:</span>
          <span>
            {subsidy.acceptance_start && (
              <>
                {new Date(subsidy.acceptance_start).toLocaleDateString('ja-JP')}
                {' 〜 '}
              </>
            )}
            {subsidy.acceptance_end && (
              <span className="font-semibold text-red-600">
                {new Date(subsidy.acceptance_end).toLocaleDateString('ja-JP')}
              </span>
            )}
          </span>
        </div>
      </div>

      {onDetailClick && (
        <button
          onClick={() => onDetailClick(subsidy.id)}
          className="mt-4 w-full bg-primary-500 hover:bg-primary-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
        >
          詳細を見る
        </button>
      )}

      <div className="mt-3 text-xs text-gray-400">
        ID: {subsidy.id}
      </div>
    </div>
  );
}
