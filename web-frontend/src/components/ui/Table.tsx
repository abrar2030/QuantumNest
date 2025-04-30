'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface TableProps extends React.HTMLAttributes<HTMLTableElement> {
  children: React.ReactNode;
}

export function Table({ className, children, ...props }: TableProps) {
  return (
    <div className="w-full overflow-auto">
      <table
        className={cn('w-full caption-bottom text-sm', className)}
        {...props}
      >
        {children}
      </table>
    </div>
  );
}

interface TableHeaderProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode;
}

export function TableHeader({ className, children, ...props }: TableHeaderProps) {
  return (
    <thead className={cn('bg-gray-50 dark:bg-gray-800', className)} {...props}>
      {children}
    </thead>
  );
}

interface TableBodyProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode;
}

export function TableBody({ className, children, ...props }: TableBodyProps) {
  return (
    <tbody className={cn('divide-y divide-gray-200 dark:divide-gray-700', className)} {...props}>
      {children}
    </tbody>
  );
}

interface TableFooterProps extends React.HTMLAttributes<HTMLTableSectionElement> {
  children: React.ReactNode;
}

export function TableFooter({ className, children, ...props }: TableFooterProps) {
  return (
    <tfoot
      className={cn('bg-gray-50 dark:bg-gray-800 font-medium text-gray-900 dark:text-gray-100', className)}
      {...props}
    >
      {children}
    </tfoot>
  );
}

interface TableRowProps extends React.HTMLAttributes<HTMLTableRowElement> {
  children: React.ReactNode;
}

export function TableRow({ className, children, ...props }: TableRowProps) {
  return (
    <tr
      className={cn(
        'hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors',
        className
      )}
      {...props}
    >
      {children}
    </tr>
  );
}

interface TableHeadProps extends React.ThHTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode;
}

export function TableHead({ className, children, ...props }: TableHeadProps) {
  return (
    <th
      className={cn(
        'h-12 px-4 text-left align-middle font-medium text-gray-500 dark:text-gray-400',
        className
      )}
      {...props}
    >
      {children}
    </th>
  );
}

interface TableCellProps extends React.TdHTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode;
}

export function TableCell({ className, children, ...props }: TableCellProps) {
  return (
    <td
      className={cn('p-4 align-middle text-gray-900 dark:text-gray-100', className)}
      {...props}
    >
      {children}
    </td>
  );
}

interface TableCaptionProps extends React.HTMLAttributes<HTMLTableCaptionElement> {
  children: React.ReactNode;
}

export function TableCaption({ className, children, ...props }: TableCaptionProps) {
  return (
    <caption
      className={cn('mt-4 text-sm text-gray-500 dark:text-gray-400', className)}
      {...props}
    >
      {children}
    </caption>
  );
}
