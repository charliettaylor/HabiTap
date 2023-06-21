<script lang="ts">
	import {
		Select,
		SelectItem,
		DatePicker,
		DatePickerInput,
		Button
	} from 'carbon-components-svelte';
	import Header from '$lib/Header.svelte';

	type Habit = {
		name: string;
		is_counted: boolean;
		id: string;
		start_date: Date;
	};
	let habits: Habit[] = [{ name: 'test', is_counted: false, start_date: new Date(), id: '1' }];
	let selected = 'test';
	$: habit = habits.find((e) => e.name === selected);
	let date = "";
</script>

<Header />

<div class="habit">
	<Select labelText="Current Habit" size="xl" bind:selected>
		{#each habits as habit}
			<SelectItem value={habit.name} />
		{/each}
	</Select>
</div>

<div class="submit">
	<DatePicker
		datePickerType="single"
		minDate={habit?.name}
        bind:value={date}
	>
		<DatePickerInput labelText="Entry Date" placeholder="mm/dd/yyyy" />
	</DatePicker>

	<Button>Submit</Button>
</div>

<style>
	.submit {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 100vw;
	}

	.habit {
		margin: 1rem;
	}
</style>
