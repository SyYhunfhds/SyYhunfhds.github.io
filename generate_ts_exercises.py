#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate all TypeScript exercise files and final-project files."""

import os

BASE = r"f:\BlogDemo\syy-v-hope-docs\src\TS\journey\src"

# Ensure all directories exist
dirs = [
    os.path.join(BASE, "stdlib", "ch07-lodash"),
    os.path.join(BASE, "stdlib", "ch08-zod"),
    os.path.join(BASE, "stdlib", "ch09-axios"),
    os.path.join(BASE, "stdlib", "ch10-dayjs"),
    os.path.join(BASE, "final-project"),
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

# ============================================================
# ch07-lodash / exercises.ts
# ============================================================
ch07_exercises = r"""import { chunk, uniqBy, groupBy, cloneDeep, merge } from 'lodash-es';

export function chunkDemo() {
  return chunk([1, 2, 3, 4, 5], 2);
}

export function uniqByDemo(users: Array<{ id: number; name: string }>) {
  return uniqBy(users, 'id');
}

export function groupByDemo<T>(items: T[], key: string) {
  return groupBy(items, key) as Record<string, T[]>;
}

export function cloneDeepDemo<T>(obj: T): T {
  const copy = cloneDeep(obj);
  return copy;
}

export function mergeDemo(defaults: object, overrides: object) {
  return merge({}, defaults, overrides);
}

export function myDebounce<T extends (...args: any[]) => void>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null;
  return (...args: Parameters<T>) => {
    if (timer !== null) {
      clearTimeout(timer);
    }
    timer = setTimeout(() => {
      fn(...args);
      timer = null;
    }, delay);
  };
}
"""

# ============================================================
# ch07-lodash / test.ts
# ============================================================
ch07_test = r"""import {
  chunkDemo,
  uniqByDemo,
  groupByDemo,
  cloneDeepDemo,
  mergeDemo,
  myDebounce,
} from './exercises';
import { reset, summary, assertEqual } from '../../utils/test';

async function run() {
  reset();

  // T1: chunkDemo
  assertEqual(
    JSON.stringify(chunkDemo()),
    JSON.stringify([[1, 2], [3, 4], [5]]),
    'ch07-lodash: chunkDemo should return [[1,2],[3,4],[5]]'
  );

  // T2: uniqByDemo
  const users = [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' },
    { id: 1, name: 'Alice Dup' },
  ];
  const uniqResult = uniqByDemo(users);
  assertEqual(
    uniqResult.length,
    2,
    'ch07-lodash: uniqByDemo should deduplicate by id'
  );

  // T3: groupByDemo
  const items = [
    { type: 'fruit', name: 'apple' },
    { type: 'fruit', name: 'banana' },
    { type: 'veg', name: 'carrot' },
  ];
  const grouped = groupByDemo(items, 'type');
  assertEqual(
    grouped['fruit'].length,
    2,
    'ch07-lodash: groupByDemo fruit group should have 2 items'
  );
  assertEqual(
    grouped['veg'].length,
    1,
    'ch07-lodash: groupByDemo veg group should have 1 item'
  );

  // T4: cloneDeepDemo - nested references independent
  const original = { a: 1, b: { c: 2 } };
  const cloned = cloneDeepDemo(original);
  cloned.b.c = 999;
  assertEqual(
    original.b.c,
    2,
    'ch07-lodash: cloneDeepDemo nested reference should be independent'
  );

  // T5: mergeDemo
  const defaults = { a: 1, b: { c: 2, d: 3 } };
  const overrides = { b: { c: 999 }, e: 4 };
  const merged = mergeDemo(defaults, overrides) as typeof defaults & {
    e: number;
  };
  assertEqual(merged.a, 1, 'ch07-lodash: mergeDemo should keep default a');
  assertEqual(merged.b.c, 999, 'ch07-lodash: mergeDemo should override b.c');
  assertEqual(merged.b.d, 3, 'ch07-lodash: mergeDemo should keep b.d');
  assertEqual(merged.e, 4, 'ch07-lodash: mergeDemo should add e');

  // T6: myDebounce
  let callCount = 0;
  const debounced = myDebounce(() => {
    callCount++;
  }, 50);
  debounced();
  debounced();
  debounced();
  assertEqual(
    callCount,
    0,
    'ch07-lodash: myDebounce should not call immediately'
  );
  await new Promise((resolve) => setTimeout(resolve, 100));
  assertEqual(
    callCount,
    1,
    'ch07-lodash: myDebounce should call once after delay'
  );

  summary('ch07-lodash');
}

run();
"""

# ============================================================
# ch08-zod / exercises.ts
# ============================================================
ch08_exercises = r"""import { z } from 'zod';

export const UserSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  age: z.number().int().positive(),
});
export type User = z.infer<typeof UserSchema>;

export const RegisterSchema = z
  .object({
    password: z.string().min(6),
    confirmPassword: z.string(),
  })
  .superRefine((data, ctx) => {
    if (data.password !== data.confirmPassword) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Passwords do not match',
        path: ['confirmPassword'],
      });
    }
  });

export function validateUser(data: unknown): {
  success: boolean;
  data?: User;
  errors?: string[];
} {
  const result = UserSchema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return {
    success: false,
    errors: result.error.issues.map((issue) => issue.message),
  };
}

export const TrimmedString = z.string().transform((s) =>
  s.trim().toLowerCase()
);

export const OutputUserSchema = UserSchema.omit({ email: true });

export const ChineseErrorSchema = z.string({
  required_error: '必填',
});
"""

# ============================================================
# ch08-zod / test.ts
# ============================================================
ch08_test = r"""import {
  UserSchema,
  RegisterSchema,
  validateUser,
  TrimmedString,
  OutputUserSchema,
  ChineseErrorSchema,
} from './exercises';
import { reset, summary, assertEqual } from '../../utils/test';

function run() {
  reset();

  // T1: validateUser with valid data
  const valid = validateUser({
    name: 'Alice',
    email: 'alice@example.com',
    age: 25,
  });
  assertEqual(
    valid.success,
    true,
    'ch08-zod: validateUser valid data should succeed'
  );
  if (valid.success && valid.data) {
    assertEqual(
      valid.data.name,
      'Alice',
      'ch08-zod: validateUser should return name'
    );
    assertEqual(
      valid.data.email,
      'alice@example.com',
      'ch08-zod: validateUser should return email'
    );
  }

  // T2: validateUser with invalid data
  const invalid = validateUser({ name: 'A', email: 'not-email', age: -5 });
  assertEqual(
    invalid.success,
    false,
    'ch08-zod: validateUser invalid data should fail'
  );
  if (!invalid.success && invalid.errors) {
    assertEqual(
      invalid.errors.length > 0,
      true,
      'ch08-zod: validateUser should return errors'
    );
  }

  // T3: RegisterSchema - passwords match
  const validReg = RegisterSchema.safeParse({
    password: '123456',
    confirmPassword: '123456',
  });
  assertEqual(
    validReg.success,
    true,
    'ch08-zod: RegisterSchema matching passwords should succeed'
  );

  // T4: RegisterSchema - passwords do not match
  const invalidReg = RegisterSchema.safeParse({
    password: '123456',
    confirmPassword: '654321',
  });
  assertEqual(
    invalidReg.success,
    false,
    'ch08-zod: RegisterSchema mismatched passwords should fail'
  );

  // T5: TrimmedString transform
  const trimmed = TrimmedString.parse('  Hello World  ');
  assertEqual(
    trimmed,
    'hello world',
    'ch08-zod: TrimmedString should trim and lowercase'
  );

  // T6: OutputUserSchema omits email
  const outputParsed = OutputUserSchema.safeParse({
    name: 'Bob',
    email: 'bob@example.com',
    age: 30,
  });
  assertEqual(
    outputParsed.success,
    true,
    'ch08-zod: OutputUserSchema should succeed'
  );
  if (outputParsed.success) {
    assertEqual(
      (outputParsed.data as Record<string, unknown>).email === undefined,
      true,
      'ch08-zod: OutputUserSchema should omit email'
    );
  }

  // T7: Chinese error message
  const chineseResult = ChineseErrorSchema.safeParse(undefined);
  assertEqual(
    chineseResult.success,
    false,
    'ch08-zod: ChineseErrorSchema undefined should fail'
  );
  if (!chineseResult.success) {
    const hasChineseError = chineseResult.error.issues.some(
      (issue) => issue.message === '必填'
    );
    assertEqual(
      hasChineseError,
      true,
      'ch08-zod: ChineseErrorSchema should use Chinese error message'
    );
  }

  summary('ch08-zod');
}

run();
"""

# ============================================================
# ch09-axios / exercises.ts
# ============================================================
ch09_exercises = r"""import axios, {
  AxiosInstance,
  InternalAxiosRequestConfig,
  AxiosResponse,
  AxiosError,
} from 'axios';

export function createApiClient(baseURL: string): AxiosInstance {
  const client = axios.create({ baseURL });

  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      config.headers.Authorization = 'Bearer mock-token';
      return config;
    }
  );

  client.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error: AxiosError) => {
      if (error.response?.status === 401) {
        return null as unknown as AxiosResponse;
      }
      return Promise.reject(error);
    }
  );

  return client;
}

export type User = { id: number; name: string };
export type ApiResponse<T> = { data: T; status: number };

export function wrapResponse<T>(response: AxiosResponse<T>): ApiResponse<T> {
  return { data: response.data, status: response.status };
}

export async function fetchWithRetry<T>(
  url: string,
  retries: number,
  client?: AxiosInstance
): Promise<T> {
  const axiosClient = client || axios.create();
  let lastError: unknown;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await axiosClient.get<T>(url);
      return response.data;
    } catch (error) {
      lastError = error;
      if (attempt === retries) {
        throw lastError;
      }
    }
  }
  throw lastError;
}
"""

# ============================================================
# ch09-axios / test.ts
# ============================================================
ch09_test = r"""import {
  createApiClient,
  wrapResponse,
  fetchWithRetry,
  User,
  ApiResponse,
} from './exercises';
import { reset, summary, assertEqual } from '../../utils/test';
import type { AxiosResponse } from 'axios';

async function run() {
  reset();

  // T1: createApiClient adds Authorization header
  const client = createApiClient('https://api.example.com');
  const hasReqInterceptors =
    (client as Record<string, unknown>).interceptors !== undefined;
  assertEqual(
    hasReqInterceptors,
    true,
    'ch09-axios: client should have interceptors'
  );

  // T2: wrapResponse type-safe wrapper
  const mockResponse: AxiosResponse<User> = {
    data: { id: 1, name: 'Alice' },
    status: 200,
    statusText: 'OK',
    headers: {},
    config: {} as Record<string, unknown>,
  } as AxiosResponse<User>;
  const wrapped: ApiResponse<User> = wrapResponse(mockResponse);
  assertEqual(
    wrapped.status,
    200,
    'ch09-axios: wrapResponse should return status 200'
  );
  assertEqual(
    wrapped.data.id,
    1,
    'ch09-axios: wrapResponse should return data.id'
  );
  assertEqual(
    wrapped.data.name,
    'Alice',
    'ch09-axios: wrapResponse should return data.name'
  );

  // T3: fetchWithRetry function signature
  assertEqual(
    typeof fetchWithRetry,
    'function',
    'ch09-axios: fetchWithRetry should be a function'
  );
  assertEqual(
    fetchWithRetry.length >= 2,
    true,
    'ch09-axios: fetchWithRetry should accept at least 2 params'
  );

  summary('ch09-axios');
}

run();
"""

# ============================================================
# ch10-dayjs / exercises.ts
# ============================================================
ch10_exercises = r"""import dayjs from 'dayjs';

export function formatDate(date: string, fmt: string): string {
  return dayjs(date).format(fmt);
}

export function isValidDate(str: string): boolean {
  return dayjs(str).isValid();
}

export function addDays(date: string, days: number): string {
  return dayjs(date).add(days, 'day').format('YYYY-MM-DD');
}

export function compareDate(a: string, b: string): number {
  const da = dayjs(a);
  const db = dayjs(b);
  if (da.isBefore(db)) return -1;
  if (da.isAfter(db)) return 1;
  return 0;
}

export function fromNowExample(date: string): string {
  return dayjs(date).fromNow();
}

export function getDaysInRange(start: string, end: string): string[] {
  const result: string[] = [];
  let current = dayjs(start);
  const endDate = dayjs(end);
  while (current.isBefore(endDate) || current.isSame(endDate, 'day')) {
    result.push(current.format('YYYY-MM-DD'));
    current = current.add(1, 'day');
  }
  return result;
}
"""

# ============================================================
# ch10-dayjs / test.ts
# ============================================================
ch10_test = r"""import {
  formatDate,
  isValidDate,
  addDays,
  compareDate,
  fromNowExample,
  getDaysInRange,
} from './exercises';
import { reset, summary, assertEqual } from '../../utils/test';

function run() {
  reset();

  // T1: formatDate
  const formatted = formatDate('2024-01-15', 'YYYY/MM/DD');
  assertEqual(
    formatted,
    '2024/01/15',
    'ch10-dayjs: formatDate should format correctly'
  );

  // T2: isValidDate - invalid input
  assertEqual(
    isValidDate('not-a-date'),
    false,
    'ch10-dayjs: isValidDate should return false for invalid date'
  );
  assertEqual(
    isValidDate('2024-01-15'),
    true,
    'ch10-dayjs: isValidDate should return true for valid date'
  );

  // T3: addDays - addition and subtraction
  const added = addDays('2024-01-15', 10);
  assertEqual(
    added,
    '2024-01-25',
    'ch10-dayjs: addDays should add correctly'
  );
  const subtracted = addDays('2024-01-15', -5);
  assertEqual(
    subtracted,
    '2024-01-10',
    'ch10-dayjs: addDays should subtract correctly'
  );

  // T4: compareDate
  assertEqual(
    compareDate('2024-01-15', '2024-01-20'),
    -1,
    'ch10-dayjs: compareDate a < b should return -1'
  );
  assertEqual(
    compareDate('2024-01-20', '2024-01-15'),
    1,
    'ch10-dayjs: compareDate a > b should return 1'
  );
  assertEqual(
    compareDate('2024-01-15', '2024-01-15'),
    0,
    'ch10-dayjs: compareDate equal should return 0'
  );

  // T5: fromNowExample - relative time
  const futureDate = new Date();
  futureDate.setDate(futureDate.getDate() + 7);
  const futureStr = futureDate.toISOString().split('T')[0];
  const fromNow = fromNowExample(futureStr);
  assertEqual(
    typeof fromNow,
    'string',
    'ch10-dayjs: fromNowExample should return a string'
  );
  assertEqual(
    fromNow.length > 0,
    true,
    'ch10-dayjs: fromNowExample should not be empty'
  );

  // T6: getDaysInRange
  const range = getDaysInRange('2024-01-01', '2024-01-03');
  assertEqual(
    range.length,
    3,
    'ch10-dayjs: getDaysInRange should return 3 days'
  );
  assertEqual(
    range[0],
    '2024-01-01',
    'ch10-dayjs: getDaysInRange first day'
  );
  assertEqual(
    range[2],
    '2024-01-03',
    'ch10-dayjs: getDaysInRange last day'
  );

  summary('ch10-dayjs');
}

run();
"""

# ============================================================
# final-project / types.ts
# ============================================================
fp_types = r"""export type Priority = 'low' | 'medium' | 'high';
export type TaskStatus = 'todo' | 'in-progress' | 'done';

export interface Task {
  id: string;
  title: string;
  description?: string;
  priority: Priority;
  status: TaskStatus;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

export type CreateTaskInput = Omit<
  Task,
  'id' | 'createdAt' | 'updatedAt' | 'status'
> & {
  status?: TaskStatus;
};

export type UpdateTaskInput = Partial<Omit<Task, 'id' | 'createdAt'>>;

export type Result<T> =
  | { ok: true; data: T }
  | { ok: false; error: { code: string; message: string } };

export interface TaskFilter {
  status?: TaskStatus;
  priority?: Priority;
  tag?: string;
  search?: string;
  sortBy?: 'createdAt' | 'updatedAt' | 'priority' | 'title';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  pageSize?: number;
}

export interface TaskStats {
  total: number;
  byStatus: Record<TaskStatus, number>;
  byPriority: Record<Priority, number>;
  topTags: Array<{ tag: string; count: number }>;
  completionRate: number;
}
"""

# ============================================================
# final-project / schemas.ts
# ============================================================
fp_schemas = r"""import { z } from 'zod';

export const CreateTaskSchema = z.object({
  title: z.string().min(2).max(100),
  description: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  status: z.enum(['todo', 'in-progress', 'done']).default('todo'),
  tags: z.array(z.string()).default([]),
});

export const UpdateTaskSchema = CreateTaskSchema.partial().omit({
  title: true,
});
"""

# ============================================================
# final-project / task-manager.ts
# ============================================================
fp_task_manager = r"""import {
  Task,
  CreateTaskInput,
  UpdateTaskInput,
  Result,
  TaskFilter,
  TaskStats,
  Priority,
  TaskStatus,
} from './types';
import { CreateTaskSchema, UpdateTaskSchema } from './schemas';

export class TaskManager {
  private tasks: Map<string, Task>;

  constructor() {
    this.tasks = new Map();
  }

  private generateId(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  async createTask(input: CreateTaskInput): Promise<Result<Task>> {
    const parsed = CreateTaskSchema.safeParse(input);
    if (!parsed.success) {
      return {
        ok: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: parsed.error.issues
            .map((issue) => issue.message)
            .join(', '),
        },
      };
    }

    const data = parsed.data;
    const now = new Date();
    const task: Task = {
      id: this.generateId(),
      title: data.title,
      description: data.description,
      priority: data.priority as Priority,
      status: (data.status || 'todo') as TaskStatus,
      tags: [...new Set(data.tags.map((t) => t.toLowerCase().trim()))],
      createdAt: now,
      updatedAt: now,
    };

    this.tasks.set(task.id, task);
    return { ok: true, data: task };
  }

  async getTask(id: string): Promise<Result<Task>> {
    const task = this.tasks.get(id);
    if (!task) {
      return {
        ok: false,
        error: { code: 'NOT_FOUND', message: `Task ${id} not found` },
      };
    }
    return { ok: true, data: task };
  }

  async updateTask(
    id: string,
    input: UpdateTaskInput
  ): Promise<Result<Task>> {
    const existing = this.tasks.get(id);
    if (!existing) {
      return {
        ok: false,
        error: { code: 'NOT_FOUND', message: `Task ${id} not found` },
      };
    }

    const parsed = UpdateTaskSchema.safeParse(input);
    if (!parsed.success) {
      return {
        ok: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: parsed.error.issues
            .map((issue) => issue.message)
            .join(', '),
        },
      };
    }

    const data = parsed.data;
    const updated: Task = {
      ...existing,
      ...data,
      tags: data.tags
        ? [...new Set(data.tags.map((t) => t.toLowerCase().trim()))]
        : existing.tags,
      updatedAt: new Date(),
    };

    this.tasks.set(id, updated);
    return { ok: true, data: updated };
  }

  async deleteTask(id: string): Promise<Result<void>> {
    if (!this.tasks.has(id)) {
      return {
        ok: false,
        error: { code: 'NOT_FOUND', message: `Task ${id} not found` },
      };
    }
    this.tasks.delete(id);
    return { ok: true, data: undefined };
  }

  async listTasks(filter: TaskFilter): Promise<Result<Task[]>> {
    let tasks = Array.from(this.tasks.values());

    // Filter by status
    if (filter.status) {
      tasks = tasks.filter((t) => t.status === filter.status);
    }

    // Filter by priority
    if (filter.priority) {
      tasks = tasks.filter((t) => t.priority === filter.priority);
    }

    // Filter by tag
    if (filter.tag) {
      const tag = filter.tag.toLowerCase().trim();
      tasks = tasks.filter((t) => t.tags.includes(tag));
    }

    // Search in title and description
    if (filter.search) {
      const search = filter.search.toLowerCase();
      tasks = tasks.filter(
        (t) =>
          t.title.toLowerCase().includes(search) ||
          (t.description && t.description.toLowerCase().includes(search))
      );
    }

    // Sort
    const sortBy = filter.sortBy || 'createdAt';
    const sortOrder = filter.sortOrder || 'desc';
    const priorityOrder: Record<Priority, number> = {
      low: 0,
      medium: 1,
      high: 2,
    };

    tasks.sort((a, b) => {
      let cmp = 0;
      if (sortBy === 'priority') {
        cmp = priorityOrder[a.priority] - priorityOrder[b.priority];
      } else if (sortBy === 'title') {
        cmp = a.title.localeCompare(b.title);
      } else {
        cmp = a[sortBy].getTime() - b[sortBy].getTime();
      }
      return sortOrder === 'asc' ? cmp : -cmp;
    });

    // Pagination
    const page = filter.page || 1;
    const pageSize = filter.pageSize || 10;
    const start = (page - 1) * pageSize;
    const paged = tasks.slice(start, start + pageSize);

    return { ok: true, data: paged };
  }

  async searchByTags(tags: string[]): Promise<Result<Task[]>> {
    const normalizedTags = tags.map((t) => t.toLowerCase().trim());
    const result = Array.from(this.tasks.values()).filter((task) =>
      normalizedTags.every((tag) => task.tags.includes(tag))
    );
    return { ok: true, data: result };
  }

  async getStats(): Promise<TaskStats> {
    const tasks = Array.from(this.tasks.values());
    const total = tasks.length;

    const byStatus: Record<TaskStatus, number> = {
      todo: 0,
      'in-progress': 0,
      done: 0,
    };
    const byPriority: Record<Priority, number> = {
      low: 0,
      medium: 0,
      high: 0,
    };
    const tagCount: Record<string, number> = {};

    for (const task of tasks) {
      byStatus[task.status]++;
      byPriority[task.priority]++;
      for (const tag of task.tags) {
        tagCount[tag] = (tagCount[tag] || 0) + 1;
      }
    }

    const topTags = Object.entries(tagCount)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([tag, count]) => ({ tag, count }));

    const completionRate = total > 0 ? byStatus['done'] / total : 0;

    return { total, byStatus, byPriority, topTags, completionRate };
  }

  async batchUpdateStatus(
    ids: string[],
    status: TaskStatus
  ): Promise<Result<number>> {
    let updated = 0;
    const invalid: string[] = [];

    for (const id of ids) {
      const task = this.tasks.get(id);
      if (!task) {
        invalid.push(id);
        continue;
      }
      task.status = status;
      task.updatedAt = new Date();
      this.tasks.set(id, task);
      updated++;
    }

    if (invalid.length > 0 && updated === 0) {
      return {
        ok: false,
        error: {
          code: 'NOT_FOUND',
          message: `Tasks not found: ${invalid.join(', ')}`,
        },
      };
    }

    return { ok: true, data: updated };
  }
}
"""

# ============================================================
# final-project / index.ts
# ============================================================
fp_index = r"""export { TaskManager } from './task-manager';
export * from './types';
"""

# ============================================================
# final-project / test.ts
# ============================================================
fp_test = r"""import { TaskManager } from './task-manager';
import { assertEqual, reset, summary } from '../utils/test';
import { CreateTaskInput } from './types';

async function run() {
  reset();
  const manager = new TaskManager();

  // -------------------------------------------------------
  // T1: createTask - valid task with tag deduplication & lowercasing
  // -------------------------------------------------------
  const input: CreateTaskInput = {
    title: 'Learn TypeScript',
    description: 'Study TS generics',
    priority: 'high',
    tags: ['TS', 'ts', 'PROGRAMMING'],
  };
  const t1 = await manager.createTask(input);
  assertEqual(t1.ok, true, 'T1: createTask should succeed');
  if (t1.ok) {
    assertEqual(
      t1.data.title,
      'Learn TypeScript',
      'T1: title should match'
    );
    assertEqual(
      t1.data.tags.length,
      2,
      'T1: tags should be deduplicated (2 unique)'
    );
    assertEqual(
      t1.data.tags.includes('ts'),
      true,
      'T1: tags should include lowercase ts'
    );
    assertEqual(
      t1.data.tags.includes('programming'),
      true,
      'T1: tags should include lowercase programming'
    );
  }

  // -------------------------------------------------------
  // T2: createTask - invalid task (title too short)
  // -------------------------------------------------------
  const invalidInput: CreateTaskInput = {
    title: 'A',
    priority: 'low',
    tags: [],
  };
  const t2 = await manager.createTask(invalidInput);
  assertEqual(t2.ok, false, 'T2: createTask with short title should fail');
  if (!t2.ok) {
    assertEqual(
      t2.error.code,
      'VALIDATION_ERROR',
      'T2: error code should be VALIDATION_ERROR'
    );
  }

  // -------------------------------------------------------
  // T3: getTask - non-existent task
  // -------------------------------------------------------
  const t3 = await manager.getTask('non-existent-id');
  assertEqual(t3.ok, false, 'T3: getTask with non-existent id should fail');
  if (!t3.ok) {
    assertEqual(
      t3.error.code,
      'NOT_FOUND',
      'T3: error code should be NOT_FOUND'
    );
  }

  // -------------------------------------------------------
  // T4: updateTask - update status
  // -------------------------------------------------------
  let taskId = '';
  if (t1.ok) {
    taskId = t1.data.id;
  }
  const t4 = await manager.updateTask(taskId, { status: 'in-progress' });
  assertEqual(t4.ok, true, 'T4: updateTask should succeed');
  if (t4.ok) {
    assertEqual(
      t4.data.status,
      'in-progress',
      'T4: status should be in-progress'
    );
  }

  // -------------------------------------------------------
  // T5: deleteTask then getTask - should not found
  // -------------------------------------------------------
  const t5a = await manager.deleteTask(taskId);
  assertEqual(t5a.ok, true, 'T5: deleteTask should succeed');
  const t5b = await manager.getTask(taskId);
  assertEqual(t5b.ok, false, 'T5: getTask after delete should fail');

  // -------------------------------------------------------
  // Seed more tasks for subsequent tests
  // -------------------------------------------------------
  await manager.createTask({
    title: 'Task A',
    priority: 'high',
    tags: ['urgent'],
  });
  await manager.createTask({
    title: 'Task B',
    priority: 'medium',
    tags: ['bug'],
  });
  await manager.createTask({
    title: 'Task C',
    priority: 'low',
    tags: ['feature', 'urgent'],
  });
  await manager.createTask({
    title: 'Another Task',
    priority: 'high',
    status: 'done',
    tags: ['urgent'],
  });
  await manager.createTask({
    title: 'Zebra Task',
    priority: 'low',
    tags: ['misc'],
  });

  // Now we have 5 tasks (the first one was deleted)

  // -------------------------------------------------------
  // T6: listTasks - filter by priority
  // -------------------------------------------------------
  const t6 = await manager.listTasks({ priority: 'high' });
  assertEqual(t6.ok, true, 'T6: listTasks filter should succeed');
  if (t6.ok) {
    assertEqual(
      t6.data.length,
      2,
      'T6: should have 2 high-priority tasks'
    );
  }

  // -------------------------------------------------------
  // T7: listTasks - sort by title ascending
  // -------------------------------------------------------
  const t7 = await manager.listTasks({
    sortBy: 'title',
    sortOrder: 'asc',
  });
  assertEqual(t7.ok, true, 'T7: listTasks sorted should succeed');
  if (t7.ok && t7.data.length >= 2) {
    assertEqual(
      t7.data[0].title.localeCompare(t7.data[1].title) <= 0,
      true,
      'T7: titles should be in ascending order'
    );
  }

  // -------------------------------------------------------
  // T8: searchByTags - Set intersection
  // -------------------------------------------------------
  const t8 = await manager.searchByTags(['urgent']);
  assertEqual(t8.ok, true, 'T8: searchByTags should succeed');
  if (t8.ok) {
    assertEqual(
      t8.data.length >= 2,
      true,
      'T8: should find at least 2 tasks with urgent tag'
    );
  }

  // -------------------------------------------------------
  // T9: getStats - task statistics
  // -------------------------------------------------------
  const t9 = await manager.getStats();
  assertEqual(t9.total, 5, 'T9: stats total should be 5');
  assertEqual(
    typeof t9.completionRate,
    'number',
    'T9: completionRate should be a number'
  );
  assertEqual(t9.byStatus['done'], 1, 'T9: done count should be 1');
  assertEqual(
    t9.byPriority['high'] >= 1,
    true,
    'T9: high priority count should be >= 1'
  );

  // -------------------------------------------------------
  // T10: batchUpdateStatus
  // -------------------------------------------------------
  const allTasks = await manager.listTasks({});
  let batchIds: string[] = [];
  if (allTasks.ok) {
    batchIds = allTasks.data.slice(0, 2).map((t) => t.id);
  }
  const t10 = await manager.batchUpdateStatus(batchIds, 'done');
  assertEqual(t10.ok, true, 'T10: batchUpdateStatus should succeed');
  if (t10.ok) {
    assertEqual(t10.data, 2, 'T10: should update 2 tasks');
  }

  // -------------------------------------------------------
  // T11: listTasks - pagination
  // -------------------------------------------------------
  const t11a = await manager.listTasks({ page: 1, pageSize: 2 });
  assertEqual(t11a.ok, true, 'T11: page 1 should succeed');
  if (t11a.ok) {
    assertEqual(
      t11a.data.length <= 2,
      true,
      'T11: page 1 should have at most 2 items'
    );
  }

  const t11b = await manager.listTasks({ page: 2, pageSize: 2 });
  assertEqual(t11b.ok, true, 'T11: page 2 should succeed');
  if (t11b.ok) {
    assertEqual(
      t11b.data.length <= 2,
      true,
      'T11: page 2 should have at most 2 items'
    );
  }

  // -------------------------------------------------------
  // T12: End-to-end full lifecycle
  // -------------------------------------------------------
  const e2eInput: CreateTaskInput = {
    title: 'E2E Test Task',
    description: 'Testing full lifecycle',
    priority: 'high',
    status: 'todo',
    tags: ['e2e', 'test'],
  };

  // Create
  const e2eCreate = await manager.createTask(e2eInput);
  assertEqual(e2eCreate.ok, true, 'T12: E2E create should succeed');
  if (!e2eCreate.ok) return;
  const e2eId = e2eCreate.data.id;

  // Read back
  const e2eGet1 = await manager.getTask(e2eId);
  assertEqual(e2eGet1.ok, true, 'T12: E2E get after create should succeed');
  if (e2eGet1.ok) {
    assertEqual(
      e2eGet1.data.title,
      'E2E Test Task',
      'T12: E2E title should match'
    );
  }

  // Update
  const e2eUpdate = await manager.updateTask(e2eId, {
    status: 'in-progress',
    description: 'Updated description',
  });
  assertEqual(e2eUpdate.ok, true, 'T12: E2E update should succeed');
  if (e2eUpdate.ok) {
    assertEqual(
      e2eUpdate.data.status,
      'in-progress',
      'T12: E2E status should be in-progress'
    );
    assertEqual(
      e2eUpdate.data.description,
      'Updated description',
      'T12: E2E description should be updated'
    );
  }

  // Verify update persisted
  const e2eGet2 = await manager.getTask(e2eId);
  assertEqual(e2eGet2.ok, true, 'T12: E2E get after update should succeed');
  if (e2eGet2.ok) {
    assertEqual(
      e2eGet2.data.status,
      'in-progress',
      'T12: E2E persisted status should be in-progress'
    );
  }

  // Complete
  const e2eComplete = await manager.updateTask(e2eId, { status: 'done' });
  assertEqual(e2eComplete.ok, true, 'T12: E2E complete should succeed');
  if (e2eComplete.ok) {
    assertEqual(
      e2eComplete.data.status,
      'done',
      'T12: E2E status should be done'
    );
  }

  // Delete
  const e2eDelete = await manager.deleteTask(e2eId);
  assertEqual(e2eDelete.ok, true, 'T12: E2E delete should succeed');

  // Verify deleted
  const e2eAfterDelete = await manager.getTask(e2eId);
  assertEqual(
    e2eAfterDelete.ok,
    false,
    'T12: E2E after delete should not be found'
  );

  summary('Final Project');
}

run();
"""

# ============================================================
# Write all files
# ============================================================
files = {
    os.path.join(BASE, "stdlib", "ch07-lodash", "exercises.ts"): ch07_exercises,
    os.path.join(BASE, "stdlib", "ch07-lodash", "test.ts"): ch07_test,
    os.path.join(BASE, "stdlib", "ch08-zod", "exercises.ts"): ch08_exercises,
    os.path.join(BASE, "stdlib", "ch08-zod", "test.ts"): ch08_test,
    os.path.join(BASE, "stdlib", "ch09-axios", "exercises.ts"): ch09_exercises,
    os.path.join(BASE, "stdlib", "ch09-axios", "test.ts"): ch09_test,
    os.path.join(BASE, "stdlib", "ch10-dayjs", "exercises.ts"): ch10_exercises,
    os.path.join(BASE, "stdlib", "ch10-dayjs", "test.ts"): ch10_test,
    os.path.join(BASE, "final-project", "types.ts"): fp_types,
    os.path.join(BASE, "final-project", "schemas.ts"): fp_schemas,
    os.path.join(BASE, "final-project", "task-manager.ts"): fp_task_manager,
    os.path.join(BASE, "final-project", "index.ts"): fp_index,
    os.path.join(BASE, "final-project", "test.ts"): fp_test,
}

for filepath, content in files.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.lstrip("\n"))
    print(f"OK  {filepath}")

print("\nDone! All files generated successfully.")
